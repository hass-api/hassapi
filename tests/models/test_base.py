from unittest.mock import patch

import pytest

from hassapi.models import base


class DummyModel(base.Model):
    pass


class DummyModelList(base.ModelList):
    def __init__(self):
        super().__init__(("a", "b"))


@patch("hassapi.models.base.asdict")
@patch("hassapi.models.base._repr_dict", return_value="dummy field repr")
def test_model_repr(mock_repr_dict, mock_asdict):
    assert repr(DummyModel()) == "DummyModel with fields:\ndummy field repr"


def test_model_list_repr():
    assert repr(DummyModelList()) == "DummyModelList with items: [\n- 'a'\n\n\n- 'b'\n\n\n]"


def test_repr_dict():
    input_dict = {"a": "b", "c": {"d": "e", "f": {"g": "h"}}}
    expected_lines = (
        "    a: b",
        "    c: ",
        "        d: e",
        "        f: ",
        "                g: h",
    )
    assert base._repr_dict(input_dict) == "\n".join(expected_lines)
