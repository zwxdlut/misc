import time

import lakefs_client
from lakefs_client.client import LakeFSClient
from lakefs_client.api import (  # noqa: F401
    branches_api,
    tags_api,
    objects_api,
    commits_api)
from lakefs_client.model.branch_creation import BranchCreation
from lakefs_client.model.tag_creation import TagCreation
from lakefs_client.model.object_stats_list import ObjectStatsList  # noqa: F401
from lakefs_client.model.path_list import PathList
from lakefs_client.model.commit_creation import CommitCreation
from lakefs_client.model.error import Error  # noqa: F401
from pprint import pprint  # noqa: F401


class LakeStorage:
    def __init__(self,
                 repo=None,
                 branch=None,
                 lakehost=None,
                 accessKey=None,
                 secretKey=None) -> None:
        # lakeFS credentials and endpoint
        configuration = lakefs_client.Configuration()
        configuration.username = accessKey
        configuration.password = secretKey
        configuration.host = lakehost
        self.client = LakeFSClient(configuration)
        self.setrepo(repo)
        self.setbranch(branch)

    def __del__(self) -> None:
        pass

    def setrepo(self, repo):
        self.repo = repo

    def setbranch(self, branch):
        self.branch = branch

    def create_branch(self, branch, source=None):
        if not source:
            source = self.branch

        try:
            # create branch
            branch_creation = BranchCreation(
                name=branch,
                source=source,
            )
            api_response = self.client.branches_api.create_branch(  # noqa
                self.repo, branch_creation)
            # pprint(api_response)
        except lakefs_client.ApiException as e:
            print("Exception when calling BranchesApi->create_branch: "
                  "%s\n" % e)

    def delete_branch(self, branch):
        try:
            # delete branch
            api_response = self.client.branches_api.delete_branch(  # noqa
                self.repo, branch)
            # pprint(api_response)
        except lakefs_client.ApiException as e:
            print("Exception when calling BranchesApi->delete_branch: "
                  "%s\n" % e)

    def list_branches(self):
        try:
            # list branches
            api_response = self.client.branches_api.list_branches(
                self.repo)
            # pprint(api_response)

            bs = []
            for r in api_response["results"]:
                bs.append(r["id"])

            return bs
        except lakefs_client.ApiException as e:
            print("Exception when calling BranchesApi->list_branches: "
                  "%s\n" % e)

    def create_tag(self, tag, branch=None):
        if not branch:
            branch = self.branch

        try:
            # create tag
            tag_creation = TagCreation(
                id=tag,
                ref=branch,
            )

            api_response = self.client.tags_api.create_tag(
                self.repo, tag_creation)
            # pprint(api_response)

            return api_response["commit_id"]
        except lakefs_client.ApiException as e:
            print("Exception when calling TagsApi->create_tag: "
                  "%s\n" % e)

    def delete_tag(self, tag):
        try:
            # delete tag
            api_response = self.client.tags_api.delete_tag(  # noqa
                self.repo, tag)
            # pprint(api_response)
        except lakefs_client.ApiException as e:
            print("Exception when calling TagsApi->delete_tag: "
                  "%s\n" % e)

    def list_tags(self):
        try:
            # list tags
            api_response = self.client.tags_api.list_tags(
                self.repo)
            # pprint(api_response)

            bs = []
            for r in api_response["results"]:
                bs.append(r["id"])

            return bs
        except lakefs_client.ApiException as e:
            print("Exception when calling TagsApi->list_tags: "
                  "%s\n" % e)

    def upload2stage(self, url, path, branch=None, timeout=-1):
        if not branch:
            branch = self.branch

        with open(path, "rb") as f:
            try:
                # upload object
                api_response = self.client.objects_api.upload_object(  # noqa
                    self.repo, branch, url, storage_class="",
                    # if_none_match="*",
                    content=f)
                # pprint(api_response)
            except lakefs_client.ApiException as e:
                print("Exception when calling ObjectsApi->upload_object:"
                      "%s\n" % e)

    def download(self, url, path, branch=None, timeout=-1):
        if not branch:
            branch = self.branch

        try:
            # get object
            api_response = self.client.objects_api.get_object(
                self.repo, branch, url)
            # pprint(api_response)

            with open(path, "wb") as f:
                f.write(api_response.read())
        except lakefs_client.ApiException as e:
            print("Exception when calling ObjectsApi->get_object:"
                  "%s\n" % e)

    def delete_objects(self, objs, branch=None):
        if not branch:
            branch = self.branch

        try:
            # delete objects
            plist = PathList(objs)
            api_response = self.client.objects_api.delete_objects(  # noqa
                self.repo, branch, plist)
            # pprint(api_response)
        except lakefs_client.ApiException as e:
            print("Exception when calling ObjectsApi->delete_objects: "
                  "%s\n" % e)

    def list_objects(self, branch=None, prefix=""):
        if not branch:
            branch = self.branch

        try:
            # list objects under a given prefix, max amount is 1000
            api_response = self.client.objects_api.list_objects(
                self.repo, branch, prefix=prefix)
            # pprint(api_response)

            objs = []
            for r in api_response["results"]:
                objs.append(r["path"])

            return objs
        except lakefs_client.ApiException as e:
            print("Exception when calling ObjectsApi->list_objects: %s\n" % e)

    def commit(self, msg, branch=None):
        if not branch:
            branch = self.branch

        try:
            # commit
            commit_creation = CommitCreation(
                message=msg,
                metadata={
                    "key": "key_example"
                },
                date=int(time.time()),
            )
            api_response = self.client.commits_api.commit(
                self.repo, branch, commit_creation)
            # pprint(api_response)

            return api_response["id"]
        except lakefs_client.ApiException as e:
            print("Exception when calling CommitsApi->commit: %s\n" % e)


# EOF
