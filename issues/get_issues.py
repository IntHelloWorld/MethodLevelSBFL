import json
import os
import re
import shutil

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

TOKEN = ""
REPO_FILE = "/root/APR/GrowingBugRepository-6.1/framework/bug-mining/bug_mining_projects_info.txt"
PROJ_DB_DIR = "/root/APR/GrowingBugRepository-6.1/framework/projects"
BUGS_INFO_FILE = "active-bugs.csv"
RESULT_FILE = "issue_info.json"

root = os.path.dirname(os.path.abspath(__file__))

def parse_repo_file(repo_file, proj_dict):
    with open(repo_file, "r") as f:
        lines = f.readlines()
    for line in lines:
        items = line.strip().split("\t")
        if not items:
            continue
        proj_id = items[0]
        owner_repo = items[2]
        owner_repo = re.search(r"github\.com/([^.]+)\.git", owner_repo).group(1)
        if proj_id not in proj_dict:
            proj_dict[proj_id] = {"owner_repo": owner_repo}


def parse_bugs_info_file(proj_id, proj_dict):
    bugs_info_file = os.path.join(PROJ_DB_DIR, proj_id, BUGS_INFO_FILE)
    if not os.path.exists(bugs_info_file):
        print(f"File not found: {bugs_info_file}")
        return
    with open(bugs_info_file, "r") as f:
        lines = f.readlines()
    for line in lines[1:]:
        items = line.strip().split(",")
        bug_id, commit_sha_buggy, commit_sha_fixed, report_id, report_url = items
        bug_info = {
            "commit_sha_buggy": commit_sha_buggy,
            "commit_sha_fixed": commit_sha_fixed,
            "report_id": report_id,
            "report_url": report_url
        }
        if "bug_infos" not in proj_dict[proj_id]:
            proj_dict[proj_id]["bug_infos"] = {}
        proj_dict[proj_id]["bug_infos"][bug_id] = bug_info


def get_issue_comments_list(comments_url):
    # curl -L \
    #     -H "Accept: application/vnd.github+json" \
    #     -H "Authorization: Bearer <YOUR-TOKEN>" \
    #     -H "X-GitHub-Api-Version: 2022-11-28" \
    #     https://api.github.com/repos/OWNER/REPO/issues/ISSUE_NUMBER/comments
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.get(comments_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the comments, status code: {response.status_code}")
    comments_list = response.json()
    return comments_list


def get_issue_data(issue_url):
    if "github.com" in issue_url and "/issues/" in issue_url:
        issue_url = issue_url.replace("https://github.com/", "https://api.github.com/repos/")
        # curl -L \
        #     -H "Accept: application/vnd.github+json" \
        #     -H "Authorization: Bearer <YOUR-TOKEN>" \
        #     -H "X-GitHub-Api-Version: 2022-11-28" \
        #     https://api.github.com/repos/OWNER/REPO/issues/ISSUE_NUMBER
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        response = requests.get(issue_url, headers=headers)
        if response.status_code != 200:
            if response.status_code == 404:
                print(f"url: {issue_url} 404 Not Found")
                return "", ""
            else:
                raise Exception(f"Failed to fetch the issue, status code: {response.status_code}")
        issue_data = response.json()
        title = issue_data["title"]
        description = issue_data["body"]
        
        # comments_url = issue_data["comments_url"]
        # comments_list = get_issue_comments_list(comments_url)
        # comments_list = []
        
        return title, description

    elif "github.com" in issue_url and "/pull/" in issue_url:
        issue_url = issue_url.replace("https://github.com/", "https://api.github.com/repos/")
        issue_url = issue_url.replace("/pull/", "/pulls/")
        # curl -L \
        #   -H "Accept: application/vnd.github+json" \
        #   -H "Authorization: Bearer <YOUR-TOKEN>" \
        #   -H "X-GitHub-Api-Version: 2022-11-28" \
        #   https://api.github.com/repos/OWNER/REPO/pulls/PULL_NUMBER
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        response = requests.get(issue_url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch the issue, status code: {response.status_code}")
        issue_data = response.json()
        title = issue_data["title"]
        description = issue_data["body"]
        
        # comments_url = issue_data["comments_url"]
        # comments_list = get_issue_comments_list(comments_url)
        # comments_list = []
        
        return title, description

    elif "sourceforge.net" in issue_url:
        response = requests.get(issue_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch the bugs report page, status code: {response.status_code}")

        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        title, description = "", ""
        
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text()
        
        ticket_content_div = soup.find('div', id='ticket_content')
        if ticket_content_div:
            description = ticket_content_div.get_text()
        
        if title == "" and description == "":
            raise Exception(f"Failed to find title and description in url: {issue_url}")
        return title, description

    elif "issues.apache.org" in issue_url:
        response = requests.get(issue_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch the bugs report page, status code: {response.status_code}")

        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        title, description = "", ""
        
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text()
        
        ticket_content_div = soup.find('div', class_='user-content-block')
        if ticket_content_div:
            description = ticket_content_div.get_text()
        
        if title == "" and description == "":
            raise Exception(f"Failed to find title and description in url: {issue_url}")
        return title, description

    elif issue_url.endswith(".json"):
        response = requests.get(issue_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch the bugs report page, status code: {response.status_code}")
        issue_data = response.json()
        title = issue_data["summary"]
        description = issue_data["summary"]
        comments = [c['content'] for c in issue_data["comments"]]
        return title, description
    
    elif "redhat" in issue_url or "openjdk" in issue_url:
        response = requests.get(issue_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch the bugs report page, status code: {response.status_code}")

        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        title, description = "", ""
        
        title_tag = soup.find("div", class_='aui-page-header-main')
        if title_tag:
            title = title_tag.get_text()
        
        ticket_content_div = soup.find('div', class_='user-content-block')
        if ticket_content_div:
            description = ticket_content_div.get_text()
        
        if title == "" and description == "":
            print(f"Warning: Failed to find title and description in url: {issue_url}")
        return title, description
    
    elif "atlassian" in issue_url:
        title, description = "", ""
        if title == "" and description == "":
            print(f"Warning: Failed to find title and description in url: {issue_url}")
        return title, description


def get_commit_data(proj_id, bug_id, owner_repo, commit_sha):
    if len(commit_sha) == 40:  # is git Vcs
        # curl -L \
        #   -H "Accept: application/vnd.github+json" \
        #   -H "Authorization: Bearer <YOUR-TOKEN>" \
        #   -H "X-GitHub-Api-Version: 2022-11-28" \
        #   https://api.github.com/repos/OWNER/REPO/commits/REF
        url = f"https://api.github.com/repos/{owner_repo}/commits/{commit_sha}"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch the comment, status code: {response.status_code}")
        comment_data = response.json()
        return comment_data["commit"]["message"]
    else:  # is svn Vcs
        buggy_dir = os.path.join(root, "buggy")
        os.system(f"defects4j checkout -p {proj_id} -v {bug_id}b -w {buggy_dir}")
        os.chdir(buggy_dir)
        commit_message = os.popen(f"svn log -r {commit_sha}").read()
        os.chdir(root)
        shutil.rmtree(buggy_dir)
        return commit_message

if __name__ == "__main__":
    if os.path.exists(os.path.join(root, RESULT_FILE)):
        with open(os.path.join(root, RESULT_FILE), "r") as f:
            proj_dict = json.load(f)
    else:
        proj_dict = {}
        parse_repo_file(REPO_FILE, proj_dict)
        for proj_id in proj_dict:
            parse_bugs_info_file(proj_id, proj_dict)
    
    # # Update owner_repo
    # new_proj_dict = {}
    # parse_repo_file(REPO_FILE, new_proj_dict)
    # for proj_id in new_proj_dict:
    #     if new_proj_dict[proj_id]["owner_repo"] != proj_dict[proj_id]["owner_repo"]:
    #         proj_dict[proj_id]["owner_repo"] = new_proj_dict[proj_id]["owner_repo"]
    
    not_exist_proj = []
    
    for proj_id in proj_dict:
        if "bug_infos" not in proj_dict[proj_id]:
            print("Warning: No bug_infos for project:", proj_id)
            not_exist_proj.append(proj_id)
            continue
        for bug_id in tqdm(proj_dict[proj_id]["bug_infos"], desc=f"Processing {proj_id}"):
            bug_info = proj_dict[proj_id]["bug_infos"][bug_id]
            if "issue_title" in bug_info and "issue_description" in bug_info:
                if bug_info["issue_title"] and bug_info["issue_description"]:
                    continue
            issue_url = bug_info["report_url"]
            owner_repo = proj_dict[proj_id]["owner_repo"]
            commit_sha_buggy = bug_info["commit_sha_buggy"]
            if issue_url.startswith("http"):
                title, description = get_issue_data(issue_url)
                bug_info["issue_title"] = title
                bug_info["issue_description"] = description
                if title == "" and description == "":
                    commit_message = get_commit_data(proj_id, bug_id, owner_repo, commit_sha_buggy)
                    bug_info["issue_title"] = commit_message
                    bug_info["issue_description"] = commit_message
            else:
                commit_message = get_commit_data(proj_id, bug_id, owner_repo, commit_sha_buggy)
                bug_info["issue_title"] = commit_message
                bug_info["issue_description"] = commit_message
            
            with open(os.path.join(root, RESULT_FILE), "w") as f:
                json.dump(proj_dict, f, indent=4)
    
    for proj_id in not_exist_proj:
        del proj_dict[proj_id]
    with open(os.path.join(root, RESULT_FILE), "w") as f:
        json.dump(proj_dict, f, indent=4)