import os

# trying to do with without running the `git` command
config = None

def get_git_version():
    global config, ref, commit_hash
    try:
        ref
    except NameError:
        # get current ref
        ref = open(".git/HEAD").read().split(":")[-1].strip()

        #get current hash
        commit_hash = open(os.path.join(".git", ref)).read().strip()

    return {
        "version": commit_hash[-8:-1],
        "full_version": commit_hash,
        "link": config["link_format_string"].format(hash=commit_hash)
    }

def get_set_version():
    global config
    return {
        "version": config["override_version"],
        "full_version": config["override_version"],
        "link": None
    }

def main(app, conf):
    global config
    config = conf
    if config["use_git"]:
        app.add_template_global(get_git_version, "get_version")
    else:
        app.add_template_global(get_set_version, "get_version")
