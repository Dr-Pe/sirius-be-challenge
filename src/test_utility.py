from src.dependencies import fs_manager
from src.main import app


def _get_all_bucket_names():
    return [b.name for b in fs_manager.clients[0].client.client.list_buckets()]


def _delete_all_files():
    for cli in fs_manager.clients:
        for bname in _get_all_bucket_names():
            for obj in cli.client.client.list_objects(bname):
                cli.client.client.remove_object(bname, obj.object_name)


def _delete_all_buckets():
    for cli in fs_manager.clients:
        for bname in _get_all_bucket_names():
            try:
                cli.destroy_bucket(bname)
            except Exception as e:
                print(e)


def test_utility():
    _delete_all_files()
    _delete_all_buckets()

    assert _get_all_bucket_names() == []
