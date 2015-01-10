import unittest


class CreateNewUserTest(unittest.TestCase):
    def test_can_create_a_new_user(self):
        # Bob types in signup page address and presses Enter. Browser
        # successfully delivers him a signup page.

        # Page title says: "MyWiki -- Sign Up". There's also a heading and a
        # form. Heading is as follows: "Create new user account".

        # Bob enters his name (bob) into "Username" field.
        #
        # Bob uses "test123" as password in "Password" field and confirms it in
        # "Verify password" field.

        # He does not specify email address, since it's optional. Bob presses
        # "Create new user" button.

        # Browser redirects Bob to the home page. He can tell that by looking at
        # page title, it says: "MyWiki -- Welcome!" He can also see his name
        # (bob) in the top area of the page.
        pass

    def test_can_not_create_user_with_empty_username(self):
        # Bob goes to signup page.

        # Bob omits the "Usename" field, fills in "test123" in both "Password"
        # and "Verify password" fields.

        # Bob clicks "Create new user" button.

        # Signup page refreshes and he can see error message next to "Username"
        # field. "Password" and "Verify password" fields are empty.
        pass

    def test_can_not_create_user_without_password(self):
        # Bob goes to signup page.

        # Bob enters his name (bob) into "Username" field.

        # He omits "Password" and "Verify password" fields and clicks "Create
        # new user" button.

        # Signup page refreshes and he can see error message next to "Password"
        # field.

        # "Username" field still has his name (bob) in it.
        pass

    def test_has_to_verify_password_to_create_a_user(self):
        # Bob goes to signup page.

        # Bob enters his name (bob) into "Username" field.

        # He enters "test123" into "Password" field.

        # He mistypes confirmation password, entering "test124" into "Verify
        # password" field.

        # Bob clicks "Create new user button".

        # Signup page refreshes and he can see error message next to "Verify
        # password" field.

        # Both "Password" and "Verify password" fields are empty. "Username"
        # field still has his name in it.
        pass