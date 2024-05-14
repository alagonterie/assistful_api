from flask import Flask

is_testing_setup_done = False
yaml_saved = False


def init_testing_filters(app: Flask, is_testing: bool) -> None:
    """
    :param app: The Flask application object.
    :param is_testing: A boolean value indicating whether the application is in testing mode.
    :return: None

    This method initializes the testing filters for the Flask application.
    It is intended to be called when the application is in testing mode.

    The method adds a `before_request` handler to the Flask application that sets up necessary configurations and resources for testing.
    The handler is responsible for:

    1. Checking if the `is_testing_setup_done` flag is already set. If it is, the handler returns without performing any further actions.
    2. Retrieving the test owner's user details using the `firebase_admin.auth.get_user_by_email` method.
    3. Retrieving the custom claims of the test owner's user.
    4. Attempting to get the organization context using the `org_repo.get` method with a predefined context and the organization ID from the custom claims.
       If an exception occurs, it indicates that the organization doesn't exist, so the handler proceeds to create a new organization.
    5. Creating a new organization with a randomly generated name using the `org_repo.insert` method.
       The organization ID is then added to the custom claims and updated for the test owner's user.
    6. Setting the `is_testing_setup_done` flag to indicate that the testing setup is completed.
    7. Handling exceptions that occur during the above steps and logging a warning message if necessary.
    8. Checking the `yaml_saved` flag, which indicates whether the YAML configuration has been saved.
       If it hasn't, a separate thread is started to save the YAML configuration using the `save_yaml` function.

    Note that this method assumes the necessary imports and global variable declarations have been set up prior to calling it.
    """
    if not is_testing:
        return

    @app.before_request
    def testing_setup() -> None:
        global is_testing_setup_done
        if is_testing_setup_done:
            return

        import random

        from firebase_admin import auth

        from shared.globals.constants import DEBUG_OWNER_EMAIL
        from repository.repo_modules import org_repo
        from shared.globals.enums import CustomClaimKeys

        try:
            test_owner = auth.get_user_by_email(DEBUG_OWNER_EMAIL)

            custom_claims = test_owner.custom_claims
            try:
                from shared.globals.objects import NO_USER_CONTEXT
                org_repo.get(NO_USER_CONTEXT, custom_claims[CustomClaimKeys.ORG_ID.value])
            except:
                from shared.globals.objects import OWNER_CONTEXT
                org_name = f"Test Organization {random.randint(100, 999)}"
                org_id = org_repo.insert(OWNER_CONTEXT, org_name)

                custom_claims[CustomClaimKeys.ORG_ID.value] = org_id
                auth.set_custom_user_claims(test_owner.uid, custom_claims)

                is_testing_setup_done = True

        except:
            app.logger.warning('Failed to set up test organization')

        global yaml_saved
        if not yaml_saved:
            yaml_saved = True

            # fire and forget save_yaml
            import threading
            thread = threading.Thread(target=save_yaml)
            thread.start()


def save_yaml():
    """
    Saves a YAML file with modified data obtained from the debug host of this API.
    """
    import requests
    from shared.globals.helpers import get_debug_docs_uri

    response = requests.get(get_debug_docs_uri())
    data = response.json()
    data['x-google-backend'] = {
        # TODO: Need to use Google Secret Manager in GCP to store creds like this.
        'address': '',
        'path_translation': 'APPEND_PATH_TO_ADDRESS'
    }

    with open('swagger.yaml', 'w') as outfile:
        import yaml
        yaml.dump(data, outfile, default_flow_style=False)
