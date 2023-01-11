Configuration
=============
xedocs can be configured using environment variables.

Global settings
---------------

.. list-table:: Title
   :widths: 25 25 50
   :header-rows: 1

    * - Name, Description , Default value, Notes
    - ``XEDOCS_ENV``, Path to a .env file to load. , ``~/.config/xedocs/config.env``., Requires python-dotenv package
    - ``XEDOCS_DATABASES, List of database names, separated by commas. , ``development_db,straxen_db``., For advanced user only.

Database Interface settings
---------------------------
These settings are specific to database interface implementations.


Utilix Interface
^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 25 50
   :header-rows: 1

    * - Name, Description , Default value, Notes
    - ``XEDOCS_UTILIX_PRIORITY``, Priorty when selecting a default (-1 to ignore) , ``1``, Smaller numbers are selected first.
    - ``XEDOCS_UTILIX_DATABASE_NAMES``, database name mapping,  ``{"straxen_db": "xedocs", "development_db": "xedocs-dev"}``, For advanced users only.

API iInterface
^^^^^^^^^^^^^

.. list-table::
   :widths: 25 25 50
   :header-rows: 1

    * - Name, Description , Default value, Notes
    - ``XEDOCS_API_PRIORITY``, Priorty when selecting a default (-1 to ignore) , ``2``, Smaller numbers are selected first.
    - ``XEDOCS_API_URL_TEMPLATE``, URL format , "{base_url}/{version}/{database}/{name}" ,
    - ``XEDOCS_API_BASE_URL``, Base URL of API server , "https://api.xedocs.yossisprojects.com",
    - ``XEDOCS_API_VERSION``, API version to use, "v1",
    - ``XEDOCS_API_AUDIENCE``, Audience for JWT token request., "https://api.cmt.xenonnt.org",
    - ``XEDOCS_API_READONLY``, Whether to request readonly token. , False,
    - ``XEDOCS_API_TOKEN``, API token to use for authentication. , None,
    - ``XEDOCS_API_USERNAME``, Username to use for authentication., None,
    - ``XEDOCS_API_PASSWORD``, Password to use for authentication., None,


Github Interface
^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 25 50
   :header-rows: 1

    * - Name, Description , Default value, Notes
    - ``XEDOCS_GITHUB_PRIORITY``, Priorty when selecting a default (-1 to ignore) , ``3``, Smaller numbers are selected first.
    - ``XEDOCS_GITHUB_REPO``, Github repository to use, "XENONnT/xedocs",
    - ``XEDOCS_GITHUB_TOKEN``, Github token to use for authentication. , None,
    - ``XEDOCS_GITHUB_USERNAME``, Username to use for authentication., None,
    - ``XEDOCS_GITHUB_PASSWORD``, Password to use for authentication., None,


Local Repo Interface
^^^^^^^^^^^^^^^^^^^^

Interface to a local repo on the filesystem.

.. list-table::
   :widths: 25 25 50
   :header-rows: 1

    * - Name, Description , Default value, Notes
    - ``XEDOCS_LOCAL_REPO_PRIORITY``, Priorty when selecting a default (-1 to ignore) , ``3``, Smaller numbers are selected first.
    - ``XEDOCS_LOCAL_REPO_PATH``, Path to local repository, None,

Mongo Interface
^^^^^^^^^^^^^^^
Interface to a generic mongodb server.

.. list-table::
   :widths: 25 25 50
   :header-rows: 1

    * - Name, Description , Default value, Notes
    - ``XEDOCS_MONGO_PRIORITY``, Priorty when selecting a default (-1 to ignore) , ``-1``, Smaller numbers are selected first.
    - ``XEDOCS_MONGO_URL``, URL to mongodb server, None, SHould include username/password if needed.
