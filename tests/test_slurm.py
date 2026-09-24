from accelerator_toolkit.schedulers.slurm import render_script


def test_render_slurm_dcu():
    profile={'backend':'dcu','runtime':{'dtk_root':'/opt/dtk'},'scheduler':{'type':'slurm','partition':'dcu','gres':'dcu:1','cpus_per_task':4,'mem':'16G'}}
    text=render_script(profile,['python','train.py'])
    assert '#SBATCH --partition=dcu' in text
    assert '#SBATCH --gres=dcu:1' in text
    assert 'source "/opt/dtk/env.sh"' in text
    assert 'exec python train.py' in text
