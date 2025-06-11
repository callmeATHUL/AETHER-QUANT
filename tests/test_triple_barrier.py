import pandas as pd
from data.features.triple_barrier import triple_barrier_labels


def test_triple_barrier_basic():
    df = pd.DataFrame({"Close": [100, 106, 95, 110, 90]})
    result = triple_barrier_labels(df, pt=0.05, sl=0.05, horizon=2)
    assert result["label"].iloc[0] == 1
    assert result["label"].iloc[1] == -1

