Testing
=======

Django-navigation is covered by tests itself and provides a specialized
`TestCase` class that can be reused to test other applications. For instance::

    from navigation.tests import NavigationTest


    class GameTest(NavigationTest):
        fixtures = ['test_data.yaml']
        urls = 'games.urls'

        def test_breadcrumbs(self):
            self.assertTitle('/', 'Games')
            self.assertTitle('/pc-linux/', 'PC / Linux')
            self.assertTitle('/pc-linux/wesnoth/', 'Battle for Wesnoth')

This example makes sure that certain titles correspond to given URLs, whatever
breadcrumb resolver(s) are involved.
