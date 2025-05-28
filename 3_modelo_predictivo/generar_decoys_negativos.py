#!/usr/bin/env python3
import os
import math
import random
import glob
import argparse
import multiprocessing as mp

import numpy as np
import pandas as pd
from tqdm import tqdm

from rdkit import Chem
from rdkit.Chem import AllChem, rdmolfiles, DataStructs
from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator

# ------------------- USR FUNCTIONS -------------------
class Atom:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = float(x), float(y), float(z)
    def getXCoordinate(self): return self.x
    def getYCoordinate(self): return self.y
    def getZCoordinate(self): return self.z

class Molecule:
    def __init__(self): self.atoms = []
    def addAtom(self, atom): self.atoms.append(atom)
    def getAtoms(self): return self.atoms
    def getAtom(self, i): return self.atoms[i]

def readPDBLigand(filepath):
    mol = Molecule()
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith(('HETATM','ATOM')):
                try:
                    x = float(line[30:38]); y = float(line[38:46]); z = float(line[46:54])
                    mol.addAtom(Atom(x,y,z))
                except: pass
    return mol

class USR:
    def CalculateCentroid(self, m):
        c = [0.0,0.0,0.0]
        atoms = m.getAtoms()
        if not atoms: return c
        for a in atoms:
            c[0]+=a.getXCoordinate(); c[1]+=a.getYCoordinate(); c[2]+=a.getZCoordinate()
        n = len(atoms)
        return [c[i]/n for i in range(3)]
    def _dist(self, a, pt):
        return math.sqrt((a.getXCoordinate()-pt[0])**2 + (a.getYCoordinate()-pt[1])**2 + (a.getZCoordinate()-pt[2])**2)
    def Moments(self, m, ref_index=None, centroid=None):
        if centroid is None: centroid = self.CalculateCentroid(m)
        pt = (centroid if ref_index is None else
              [m.getAtom(ref_index).getXCoordinate(), m.getAtom(ref_index).getYCoordinate(), m.getAtom(ref_index).getZCoordinate()])
        dists = [math.sqrt((atom.getXCoordinate()-pt[0])**2 + (atom.getYCoordinate()-pt[1])**2 + (atom.getZCoordinate()-pt[2])**2)
                 for atom in m.getAtoms()]
        if not dists:
            return (0.0, 0.0, 0.0)
        mean = sum(dists)/len(dists)
        var = sum((d-mean)**2 for d in dists)/len(dists)
        skew = sum(abs(d-mean)**3 for d in dists)/len(dists)
        return mean, var, (skew/(var**1.5) if var>0 else 0.0)

def getUSRDescriptor(mol):
    if not mol.getAtoms(): return None
    usr = USR()
    c = usr.CalculateCentroid(mol)
    dlist = [(i, usr._dist(mol.getAtom(i), c)) for i in range(len(mol.getAtoms()))]
    dlist.sort(key=lambda x: x[1])
    i_min, i_max = dlist[0][0], dlist[-1][0]
    far_pt = [mol.getAtom(i_max).getXCoordinate(), mol.getAtom(i_max).getYCoordinate(), mol.getAtom(i_max).getZCoordinate()]
    d2 = [(i, math.sqrt((mol.getAtom(i).getXCoordinate()-far_pt[0])**2 + (mol.getAtom(i).getYCoordinate()-far_pt[1])**2 + (mol.getAtom(i).getZCoordinate()-far_pt[2])**2))
          for i in range(len(mol.getAtoms()))]
    d2.sort(key=lambda x: x[1])
    i_ffa = d2[-1][0]
    feats = []
    feats += usr.Moments(mol, centroid=c)
    feats += usr.Moments(mol, ref_index=i_min)
    feats += usr.Moments(mol, ref_index=i_max)
    feats += usr.Moments(mol, ref_index=i_ffa)
    return feats

def smiles_to_pdb(smi, outp):
    mol = Chem.AddHs(Chem.MolFromSmiles(smi))
    if mol is None or AllChem.EmbedMolecule(mol, randomSeed=42) != 0:
        return False
    AllChem.UFFOptimizeMolecule(mol)
    if mol.GetNumAtoms() == 0:
        return False
    w = rdmolfiles.PDBWriter(outp)
    w.write(mol)
    w.close()
    return True

def usr_similarity(vec1, vec2):
    return 1.0/(1.0 + np.sum(np.abs(np.array(vec1)-np.array(vec2))) / len(vec1))

# Globals para procesos paralelos
fpgen = None
zinc_fps = []
zinc_smiles = []
used_negatives = None
lock = None
skipped_ligands = None

def init_worker(_fpgen, _fps, _smis, _used, _lock, _skipped):
    global fpgen, zinc_fps, zinc_smiles, used_negatives, lock, skipped_ligands
    fpgen = _fpgen
    zinc_fps = _fps
    zinc_smiles = _smis
    used_negatives = _used
    lock = _lock
    skipped_ligands = _skipped

def generate_one(args):
    lig_id, lig_smi, usr_l, tmp_dir, tanimoto_thr, usrr_thr = args
    mol_ref = Chem.MolFromSmiles(lig_smi)
    if mol_ref is None:
        skipped_ligands.append(lig_id)
        return None
    fp_ref = fpgen.GetFingerprint(mol_ref)
    sims = DataStructs.BulkTanimotoSimilarity(fp_ref, zinc_fps)
    attempts = 0
    max_attempts = 10000
    for smi_z, sim in zip(zinc_smiles, sims):
        attempts += 1
        if attempts > max_attempts:
            skipped_ligands.append(lig_id)
            return None
        if sim >= tanimoto_thr:
            continue
        with lock:
            cnt = used_negatives.get(smi_z, 0)
            if cnt >= 4:
                continue
        pdbp = os.path.join(tmp_dir, 'temp.pdb')
        if not smiles_to_pdb(smi_z, pdbp):
            continue
        mol_z = readPDBLigand(pdbp)
        usr_z = getUSRDescriptor(mol_z)
        if usr_z is None:
            continue
        sim_usr = usr_similarity(usr_l, usr_z)
        if sim_usr < usrr_thr:
            with lock:
                used_negatives[smi_z] = cnt + 1
            rec = {'ligando_id': lig_id, 'smiles_pos': lig_smi, 'smiles_neg': smi_z,
                   'tanimoto': sim, 'usrr_sim': sim_usr}
            for i, v in enumerate(usr_l, start=1): rec[f'USR_pos_{i}'] = v
            for i, v in enumerate(usr_z, start=1): rec[f'USR_neg_{i}'] = v
            return rec
    skipped_ligands.append(lig_id)
    return None

if __name__ == '__main__':
    print(">>> Script iniciado")
    parser = argparse.ArgumentParser()
    parser.add_argument('--uri_path', required=True)
    parser.add_argument('--input_csv', required=True)
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--chunk_size', type=int, default=500)
    parser.add_argument('--tanimoto_thr', type=float, default=0.6)
    parser.add_argument('--usrr_thr', type=float, default=0.6)
    parser.add_argument('--n_procs', type=int, default=32)
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    tmp_dir = os.path.join(args.output_dir, 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    
    with open(args.uri_path) as f:
        uris = [u.strip() for u in f if u.strip()]
    
    all_smiles = []
    for uri in tqdm(uris, desc='wget'):
        outp = os.path.join(tmp_dir, os.path.basename(uri))
        if os.system(f"wget -q -O {outp} {uri}") != 0:
            print(f"Fallo al descargar {uri}")
            continue
        for fp in glob.glob(os.path.join(tmp_dir, '*.smi')):
            with open(fp) as fi:
                all_smiles += [l.split()[0] for l in fi if l.strip()]
            os.remove(fp)
    
    raw = random.sample(all_smiles, min(100000, len(all_smiles)))
    
    # ----------------- Fingerprint optimizado -----------------
    print(">>> Procesando SMILES válidos y generando fingerprints...")
    fpgen = GetMorganGenerator(radius=2, fpSize=2048)
    zinc_mols = [(smi, Chem.MolFromSmiles(smi)) for smi in raw]
    zinc_mols = [(smi, m) for smi, m in zinc_mols if m is not None]

    zinc_smiles = [smi for smi, _ in zinc_mols]
    zinc_fps = [fpgen.GetFingerprint(m) for _, m in tqdm(zinc_mols, desc='Fingerprinting')]
    print(f">>> Se procesaron {len(zinc_fps)} SMILES válidos.")
    
    manager = mp.Manager()
    used_negatives = manager.dict()
    lock = manager.Lock()
    skipped_ligands = manager.list()
    
    df = pd.read_csv(args.input_csv)
    lig_pos = [(row['instancia'], row['Ligand_smiles'], [row[f'USR_{i}'] for i in range(1,13)]) for _,row in df.iterrows()]
    
    pool = mp.Pool(args.n_procs, initializer=init_worker, initargs=(fpgen, zinc_fps, zinc_smiles, used_negatives, lock, skipped_ligands))
    all_results = []
    
    for i in range(0, len(lig_pos), args.chunk_size):
        chunk = lig_pos[i:i+args.chunk_size]
        part = i // args.chunk_size + 1
        part_file = os.path.join(args.output_dir, f'part_{part}.csv')
        if os.path.exists(part_file):
            print(f"Skipping chunk {part}")
            all_results.extend(pd.read_csv(part_file).to_dict('records'))
            continue
        results = list(tqdm(pool.imap(generate_one, [(lid,smi,usr,tmp_dir,args.tanimoto_thr,args.usrr_thr) for lid,smi,usr in chunk]),
                             total=len(chunk), desc=f'chunk {part}'))
        records = [r for r in results if r]
        unique = {}
        for r in records:
            if r['smiles_neg'] not in unique:
                unique[r['smiles_neg']] = r
        pd.DataFrame(unique.values()).to_csv(part_file, index=False)
        all_results.extend(unique.values())
    
    pool.close(); pool.join()
    
    unique_all = {}
    for r in all_results:
        if r['smiles_neg'] not in unique_all:
            unique_all[r['smiles_neg']] = r
    pd.DataFrame(unique_all.values()).to_csv(os.path.join(args.output_dir, 'negatives_full.csv'), index=False)
    print("Done. Check outputs in", args.output_dir)
