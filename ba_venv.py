#!/usr/bin/env python

import argparse
import virtualenv
import os
import pip
import shutil
import git
import fnmatch
import tarfile
import logging


def main():
   parser = argparse.ArgumentParser()
   parser.add_argument("-r", "--repo", help="model repository url")
   parser.add_argument("-d", "--directory", help="directory to be included")
   parser.add_argument("-i", "--ignore", action='append', help="pattern to be ignore (e.g. *pyc")
   args = parser.parse_args()
   
   repo_name = get_reponame(args.repo)
   working_path = os.path.join("/home/builder/", repo_name, "workspace")

   # Delete previous build
   if os.path.isdir(working_path):
      shutil.rmtree(working_path)
   
   # Clone repo
   logging.info("=== Cloning repo ===")
   repo = git.Repo.clone_from(args.repo, os.path.join(working_path, repo_name))
   logging.info("=== Cloning repo: SUCCESSFUL ===")
 
   # Create a new venv and activate it
   virtualenv.create_environment(os.path.join(working_path, "venv"))
   execfile(os.path.join(working_path, "venv/bin/activate_this.py"), dict(__file__=os.path.join(working_path, "venv/bin/activate_this.py")))

   # Install requirements
   filepath = find_file(os.path.join(working_path, repo_name))
   install_requirements(filepath, os.path.join(working_path, "venv"))

   # Copy selected folder to the virtualenv
   directory_path = find_dir(working_path, args.directory)
   logging.info("=== Copying model directory ===")
   copy_folder_to_venv(directory_path, os.path.join(working_path, "venv", args.directory), shutil.ignore_patterns(args.ignore))
   logging.info("=== Copying model directory: SUCCESSFUL ===")
  
   # Tar.gz venv folder
   logging.info("=== Archiving venv ===")
   archieve_venv(repo_name, os.path.join(working_path, "venv"))
   logging.info("=== Archiving venv: SUCCESSFUL ===")


def get_reponame(https_url):
   '''
   This method returns repository name for an input 
   :https_url formed https://domain.com/<organization>/repository_name.git
   '''
   url = https_url.replace("https://" , "")
   return url.split('/')[2].replace(".git", "")


def find_file(path='/', name='requirements.txt'):
   for root, dirnames, filenames in os.walk(path):
         for filename in filenames:
            if filename == name:
               return os.path.join(root, filename)


def find_dir(path='/', name='model'):
   for root, dirnames, filenames in os.walk(path):
         for dirname in dirnames:
            if dirname == name:
               return os.path.join(root, dirname)


def install_requirements(file_path, install_path):
   '''
   This method search inside a :path for requirements.txt file and iterates
   it, installing every package.
   '''
   requirements_file = open(file_path,"r")
   for package in requirements_file:
      pip.main(["install", "--prefix", install_path,  package])


def archieve_venv(filename, venv_path):
   '''
   This method archieves a venv defined on :venv_path, producing a tar.gz file
   with the :filename provided
   ''' 
   with tarfile.open(filename + '.tar.gz', 'w:gz') as tarf:
      tarf.add(venv_path, arcname=os.path.basename(venv_path))
      tarf.close()


def copy_folder_to_venv(src, dst, ignore=None):
   shutil.copytree(src, dst)


if __name__ == "__main__":
    main()
