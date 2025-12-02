from setuptools import setup, find_packages
import os

# Read the contents of the README file
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Custom installation and development commands
from setuptools.command.install import install
from setuptools.command.develop import develop

class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        # Custom post-installation actions can be placed here

class CustomDevelopCommand(develop):
    def run(self):
        develop.run(self)
        # Custom post-development actions can be placed here

setup(
    name='multimodal-recommender-system-netflix',
    version='1.0.0',
    author='Netflix AI Team',
    author_email='ai-research@netflix.com',
    description='A multimodal recommender system enhancement project for Netflix',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/Multimodal-Recommender-System-Netflix',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        'numpy',
        'pandas',
        'scikit-learn',
        'duckdb',
        'matplotlib',
    ],
    extras_require={
        'dev': [
            'pytest',
            'black',
            'flake8',
            'mypy',
            'pre-commit',
        ],
    },
    entry_points={
        'console_scripts': [
            'run-experiment-personalization=experiments.experiment_personalization:run_experiment',
            'run-experiment-nlp=experiments.experiment_nlp:run_experiment',
            'run-experiment-cv=experiments.experiment_cv:run_experiment',
            'run-experiment-rl=experiments.experiment_rl:run_experiment',
            'run-experiment-multimodal=experiments.experiment_multimodal:run_experiment',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Java',
        'Programming Language :: C++',
        'Programming Language :: Go',
        'Programming Language :: Rust',
        'Programming Language :: Swift',
        'Programming Language :: Julia',
        'Programming Language :: Haskell',
        'Programming Language :: JavaScript',
        'Programming Language :: R',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
    },
    data_files=[
        ('data', ['data/sample_data.csv', 'data/sample/synthetic_viewing_history.csv']),
        ('config', ['config/config.json']) if os.path.exists('config/config.json') else ('config', []),
    ],
    package_data={
        '': ['*.txt', '*.rst', '*.md'],
        'data_preprocessing': ['*.py'],
        'recommender_systems': ['*.py'],
        'models': ['*.py'],
        'optimization': ['*.py'],
        'experiments': ['*.py'],
        'utilities': ['*.py', '*.go'],
        'analysis': ['*.R', '*.hs'],
    },
    scripts=[
        script
        for script in [
            'scripts/data_preprocessing.sh',
            'scripts/model_training.sh',
            'scripts/evaluation.sh',
        ]
        if os.path.exists(script)
    ],
)
