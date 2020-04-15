import copy

from app.models import db, Testdata, TestdataArchive


def upload_to_cloud():
    datas_raw = Testdata.query.all()
    datas_rdy = list()
    for item in datas_raw:
        # entry = copy.deepcopy(item.__dict__)
        entry = item.__dict__
        entry.pop('_sa_instance_state')
        datas_rdy.append(entry)
    # print(datas_rdy)
    



def handle_upload():
    pass

