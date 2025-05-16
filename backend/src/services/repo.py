from github import Github
import base64

class repo:
    def __init__(self, token):
        """
        Initialize with a GitHub personal access token.
        """
        self.github = Github(token)
        self.user = self.github.get_user()

    def create(self, repo_name, private=True):
        """
        Create a GitHub repository.

        :param repo_name: Name of the new repository
        :param private: Whether the repository should be private
        :return: Repository object
        """
        try:
            repo = self.user.create_repo(name=repo_name, private=private)
            print(f"Repository '{repo_name}' created successfully.")
            return repo
        except Exception as e:
            print(f"Error creating repository: {e}")
            return None

    def commit_file(self, repo, file_path, file_content, commit_message="Initial commit"):
        """
        Commit a file to the given repository.

        :param repo: Repository object
        :param file_path: Path in the repo where the file should be stored (e.g. 'README.md')
        :param file_content: Content of the file as a string
        :param commit_message: Commit message
        """
        try:
            repo.create_file(path=file_path, message=commit_message, content=file_content)
            print(f"File '{file_path}' committed successfully.")
        except Exception as e:
            print(f"Error committing file: {e}")