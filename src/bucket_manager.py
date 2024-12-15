from user_manager import UserManager

class BucketManager:

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def upload_file(self, fs_client, file_path, file_name):
        um = UserManager(self.user)
        if um.can_upload_file():
            new_quota = fs_client.upload_file(
                self.user.username, file_path, file_name)
            um.update_user_quota(new_quota)

            return new_quota
        else:
            return False

    def delete_file(self, fs_client, file_name):
        new_quota = fs_client.delete_file(self.user.username, file_name)
        UserManager(self.user).update_user_quota(new_quota)

        return new_quota
