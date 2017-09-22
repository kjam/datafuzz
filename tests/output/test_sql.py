import os
import pytest
import dataset as dataset_db

from datafuzz.dataset import DataSet

@pytest.mark.parametrize('input_obj,kwargs',[
    ([{'a': 1, 'b': 2, 'c': 3},
      {'a': 2, 'b': 3, 'c': 4},], {'output': 'sql', 'db_uri': 'sqlite:///tests/data/test_output.db',
                                   'table': 'test', 'pandas': False}),
    ([{'a': 1, 'b': 2, 'c': 3},
      {'a': 2, 'b': 3, 'c': 4},], {'output': 'sql', 'db_uri': 'sqlite:///tests/data/test_output.db',
                                   'table': 'test'}),
 ])
def test_output_sql(input_obj, kwargs):
    data = DataSet(input_obj, **kwargs)
    assert isinstance(data, DataSet)
    assert data.db_uri == kwargs.get('db_uri')
    data.to_output()

    db = dataset_db.connect(kwargs.get('db_uri'))
    rows = list(db.query('select * from test;'))
    assert len(rows) == 2
    # removing id
    assert sorted(list(rows[0].values())[1:]) == sorted(list(input_obj[0].values()))

    if os.path.exists(kwargs.get('db_uri').replace('sqlite:///', '')):
        os.remove(kwargs.get('db_uri').replace('sqlite:///', ''))

