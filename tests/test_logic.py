import pandas as pd
import os
import sys
from unittest.mock import MagicMock, patch

# Add the root directory to sys.path to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app

def test_get_mock_data():
    df = app.get_mock_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Resident Name" in df.columns
    assert "Total Score" in df.columns
    assert "Flag Status" in df.columns

@patch.dict(os.environ, {"MOCK_MODE": "true"})
def test_load_data_mock_mode():
    df = app.load_data()
    assert len(df) == 5
    assert df.iloc[0]["Resident Name"] == "Alice Smith"

def test_flagging_logic():
    df = app.get_mock_data()
    # Check if we can identify RED and AMBER flags as per app.py logic
    # total   = len(df[RESIDENT_COL].unique()) if RESIDENT_COL in df.columns else len(df)
    # flagged = len(df[df[FLAG_COL].str.upper().str.contains("RED|AMBER", na=False)]) if FLAG_COL in df.columns else 0

    FLAG_COL = "Flag Status"
    flagged = df[df[FLAG_COL].str.upper().str.contains("RED|AMBER", na=False)]
    assert len(flagged) == 3 # Bob (RED), Charlie (AMBER), Eve (AMBER)

    red = df[df[FLAG_COL].str.upper() == "RED"]
    assert len(red) == 1
    assert red.iloc[0]["Resident Name"] == "Bob Jones"

    amber = df[df[FLAG_COL].str.upper() == "AMBER"]
    assert len(amber) == 2
