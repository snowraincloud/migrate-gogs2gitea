import json
import os

import requests

# gogs api: https://github.com/gogs/docs-api
# gitea api: https://docs.gitea.com/api/1.20/#tag/repository/operation/createCurrentUserRepo

GOGS_URL = "https://gogs.example.com/api/v1/"
GOGS_ACCESS_TOKEN = "your_gogs_access_token"
GOGS_GIT_URL = "https://%s@gogs.example.com/%s/%s.git"

Gitea_URL = "https://gitea.com/api/v1/"
Gitea_ACCESS_TOKEN = "your_gitea_access_token"
Gitea_GIT_URL = "https://%s@gitea.com/%s/%s.git"


def resolve(c, o):
    if type(o) in dict:
        c.__dict__ = o
    else:
        c.__dict__ = json.loads(o)


class Gogs:
    def __init__(self, url, access_token):
        self.url = url.strip("/")
        self.access_token = access_token
        self.headers = {"Authorization": "token %s" % self.access_token}

    def get(self, url):
        r = requests.get(self.url + url, headers=self.headers)
        try:
            resp = r.json()
        except:
            print(r.status_code, r.text)
            raise
        return resp

    def getUsers(self):
        """
        [{
          "id": 1,
          "username": "unknwon",
          "full_name": "",
          "email": "fake@local",
          "avatar_url": "/avatars/1"
        }]
        """
        return self.get("/users/search?q=%&limit=100")["data"]

    def getRepos(self):
        """
        [{
            "id": 3,
            "owner": {
                "id": 12,
                "login": "Pomelo",
                "full_name": "\u9752\u67da\u5de5\u4f5c\u5ba4",
                "email": "",
                "avatar_url": "https://qingyou.njupt.edu.cn/git/avatars/12",
                "username": "Pomelo"
            },
            "name": "Graduate_BE",
            "full_name": "Pomelo/Graduate_BE",
            "description": "\u7814\u7a76\u751f\u7248\u5c0f\u7a0b\u5e8f\u540e\u7aef",
            "private": true,
            "fork": false,
            "parent": null,
            "empty": false,
            "mirror": false,
            "size": 24576,
            "html_url": "https://qingyou.njupt.edu.cn/git/Pomelo/Graduate_BE",
            "ssh_url": "ssh://gogs@qingyou.njupt.edu.cn:2222/Pomelo/Graduate_BE.git",
            "clone_url": "https://qingyou.njupt.edu.cn/git/Pomelo/Graduate_BE.git",
            "website": "",
            "stars_count": 3,
            "forks_count": 0,
            "watchers_count": 5,
            "open_issues_count": 0,
            "default_branch": "master",
            "created_at": "2017-11-07T18:06:24+08:00",
            "updated_at": "2017-11-07T20:43:11+08:00"
        }]
        """
        return self.get("/user/repos")


class Gitea:
    def __init__(self, url, access_token):
        self.url = url.strip("/")
        self.access_token = access_token
        self.headers = {"Authorization": "Bearer %s" % self.access_token}

    def get(self, url):
        r = requests.get(self.url + url, headers=self.headers)
        try:
            resp = r.json()
        except:
            print(r.status_code, r.text)
            raise
        return resp

    def post(self, url, json_data):
        r = requests.post(self.url + url, headers=self.headers, json=json_data)
        try:
            resp = r.json()
        except:
            print(r.status_code, r.text)
            raise
        return resp

    def createRepo(self, gogs_repo):
        repo = {
  "auto_init": False,
  "default_branch": gogs_repo['default_branch'],
  "description": gogs_repo["description"],
  "name": gogs_repo['name'],
  "private": gogs_repo['private'],
  "template": False,
  "trust_model": "default"
}
        return self.post("/user/repos", repo)

    def copyRepo(self, gogs):
        username = gogs["owner"]["username"]
        reponame = gogs["name"]
        fullname = gogs["full_name"]
        dirname = "tmp/%s" % fullname
        gogs_repo_git_url = GOGS_GIT_URL % (GOGS_ACCESS_TOKEN, username, reponame)
        gitea_repo_git_url = Gitea_GIT_URL % (Gitea_ACCESS_TOKEN, username, reponame)
        commands = [
            "git clone --mirror %s %s" % (gogs_repo_git_url, dirname),
            "pushd %s" % dirname.replace("/", "\\"),
            "git remote set-url origin %s" % gitea_repo_git_url,
            "git push --mirror",
            "popd"
        ]
        print(commands)
        command = " && ".join(commands)
        os.system(command)


if __name__ == '__main__':
    gogs = Gogs(GOGS_URL, GOGS_ACCESS_TOKEN)
    Gitea = Gitea(Gitea_URL, Gitea_ACCESS_TOKEN)

    # gogs_users = gogs.getUsers()
    # for gogs_user in gogs_users:
    #     print(json.dumps(gogs_user, indent=4))

    # git push --mirror的话，Gitea会自动创建
    gogs_repos = gogs.getRepos()
    for gogs_repo in gogs_repos:
        print(json.dumps(gogs_repo, indent=4))
        print(Gitea.createRepo(gogs_repo))

    for gogs_repo in gogs_repos:
        Gitea.copyRepo(gogs_repo)