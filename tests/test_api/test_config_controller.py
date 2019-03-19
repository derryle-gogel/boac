"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

from tests.util import override_config

asc_advisor_uid = '1081940'


class TestConfigController:
    """Config API."""

    def test_anonymous_api_config_request(self, client):
        """Returns a well-formed response."""
        response = client.get('/api/config')
        assert response.status_code == 200
        assert 'boacEnv' in response.json
        # In tests, certain configs are omitted or disabled (e.g., Google Analytics)
        data = response.json
        assert data['ebEnvironment'] is None
        assert data['googleAnalyticsId'] is False
        assert '@' in data['supportEmailAddress']
        assert data['featureFlagEditNotes'] is True

    def test_anonymous_api_version_request(self, client):
        """Returns a well-formed response."""
        response = client.get('/api/version')
        assert response.status_code == 200
        assert 'version' in response.json
        assert 'build' in response.json

    def test_demo_mode_on(self, app, client):
        """Demo-mode/blur is on."""
        with override_config(app, 'DEMO_MODE_AVAILABLE', True):
            assert client.get('/api/config').json.get('isDemoModeAvailable')

    def test_demo_mode_off(self, app, client):
        """Demo-mode/blur is off."""
        with override_config(app, 'DEMO_MODE_AVAILABLE', False):
            assert not client.get('/api/config').json.get('isDemoModeAvailable')
