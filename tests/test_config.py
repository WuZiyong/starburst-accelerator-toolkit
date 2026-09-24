from pathlib import Path

from accelerator_toolkit.config import deep_merge, load_yaml


def test_deep_merge_nested():
    assert deep_merge({'a':{'b':1,'c':2}}, {'a':{'b':3}}) == {'a':{'b':3,'c':2}}


def test_starburst_profiles_parse():
    root=Path(__file__).resolve().parents[1]
    for rel in ('profiles/starburst/comput1-cuda.yaml','profiles/starburst/comput2-dcu.yaml'):
        data=load_yaml(root/rel)
        assert data['backend'] in {'cuda','dcu'}
        assert data['scheduler']['type']=='slurm'
