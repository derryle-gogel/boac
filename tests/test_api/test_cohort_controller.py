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

from boac.models.cohort_filter import CohortFilter
import pytest
import simplejson as json
from tests.test_api.api_test_utils import all_cohorts_owned_by

admin_uid = '2040'
asc_advisor_uid = '1081940'
coe_advisor_uid = '1133399'


@pytest.fixture()
def admin_login(fake_auth):
    fake_auth.login(admin_uid)


@pytest.fixture()
def asc_advisor_login(fake_auth):
    fake_auth.login(asc_advisor_uid)


@pytest.fixture()
def coe_advisor_login(fake_auth):
    fake_auth.login(coe_advisor_uid)


@pytest.fixture()
def asc_owned_cohort():
    cohorts = all_cohorts_owned_by(asc_advisor_uid)
    return next((c for c in cohorts if c['name'] == 'All sports'), None)


@pytest.fixture()
def coe_owned_cohort():
    cohorts = all_cohorts_owned_by(coe_advisor_uid)
    return next((c for c in cohorts if c['name'] == 'Radioactive Women and Men'), None)


class TestCohortDetail:
    """Cohort API."""

    def test_my_cohorts_not_authenticated(self, client):
        """Rejects anonymous user."""
        response = client.get('/api/cohorts/my')
        assert response.status_code == 401

    def test_my_cohorts(self, coe_advisor_login, client):
        """Returns user's cohorts."""
        response = client.get('/api/cohorts/my')
        assert response.status_code == 200
        cohorts = response.json
        assert len(cohorts) == 2
        for key in 'name', 'alertCount', 'criteria', 'totalStudentCount', 'isOwnedByCurrentUser':
            assert key in cohorts[0], f'Missing cohort element: {key}'

    def test_students_with_alert_counts(self, asc_advisor_login, client, create_alerts, db_session):
        """Pre-load students into cache for consistent alert data."""
        from boac.models.alert import Alert

        assert client.get('/api/student/by_uid/61889').status_code == 200
        assert client.get('/api/student/by_uid/98765').status_code == 200

        Alert.update_all_for_term(2178)
        cohorts = all_cohorts_owned_by(asc_advisor_uid)
        assert len(cohorts)
        cohort_id = cohorts[0]['id']
        response = client.get(f'/api/cohort/{cohort_id}/students_with_alerts')
        assert response.status_code == 200
        students_with_alerts = response.json
        assert len(students_with_alerts) == 3

        deborah = students_with_alerts[0]
        assert deborah['sid'] == '11667051'
        assert deborah['alertCount'] == 3
        # Summary student data is included with alert counts, but full term feeds are not.
        assert deborah['cumulativeGPA'] == 3.8
        assert deborah['cumulativeUnits'] == 101.3
        assert deborah['expectedGraduationTerm']['name'] == 'Fall 2019'
        assert deborah['level'] == 'Junior'
        assert len(deborah['majors']) == 2
        assert deborah['term']['enrolledUnits'] == 12.5
        assert deborah['termGpa'][0]['gpa'] == 2.9
        assert 'enrollments' not in deborah['term']

        dave_doolittle = students_with_alerts[1]
        assert dave_doolittle['sid'] == '2345678901'
        assert dave_doolittle['uid']
        assert dave_doolittle['firstName']
        assert dave_doolittle['lastName']
        assert dave_doolittle['alertCount'] == 1

        def _get_alerts(uid):
            _response = client.get(f'/api/student/by_uid/{uid}')
            assert _response.status_code == 200
            return _response.json['notifications']['alert']

        alert_to_dismiss = _get_alerts(61889)[0]['id']
        client.get('/api/alerts/' + str(alert_to_dismiss) + '/dismiss')
        alert_to_dismiss = _get_alerts(98765)[0]['id']
        client.get('/api/alerts/' + str(alert_to_dismiss) + '/dismiss')

        students_with_alerts = client.get(f'/api/cohort/{cohort_id}/students_with_alerts').json
        assert len(students_with_alerts) == 2
        assert students_with_alerts[0]['sid'] == '11667051'
        assert students_with_alerts[0]['alertCount'] == 2

    def test_cohorts_all(self, asc_advisor_login, client):
        """Returns all cohorts per owner."""
        response = client.get('/api/cohorts/all')
        assert response.status_code == 200
        api_json = response.json
        count = len(api_json)
        assert count == 2
        for index, entry in enumerate(api_json):
            user = entry['user']
            if 0 < index < count:
                # Verify order
                assert user['name'] > api_json[index - 1]['user']['name']
            assert 'uid' in user
            cohorts = entry['cohorts']
            cohort_count = len(cohorts)
            for c_index, cohort in enumerate(cohorts):
                if 0 < c_index < cohort_count:
                    # Verify order
                    assert cohort['name'] > cohorts[c_index - 1]['name']
                assert 'id' in cohort

    def test_get_cohort(self, coe_advisor_login, client, coe_owned_cohort, create_alerts):
        """Returns a well-formed response with filtered cohort and alert count per student."""
        cohort_id = coe_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert cohort['id'] == cohort_id
        assert cohort['name'] == coe_owned_cohort['name']
        assert 'students' in cohort
        assert cohort['students'][0].get('alertCount') == 3

    def test_get_cohort_without_students(self, coe_advisor_login, client, coe_owned_cohort):
        """Returns a well-formed response with cohort and no students."""
        cohort_id = coe_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}?includeStudents=false')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert 'students' not in cohort

    def test_unauthorized_get_cohort(self, asc_advisor_login, client, coe_owned_cohort):
        """Returns a well-formed response with custom cohort."""
        cohort_id = coe_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 404
        assert 'No cohort found' in json.loads(response.data)['message']

    def test_undeclared_major(self, asc_advisor_login, client):
        """Returns a well-formed response with custom cohort."""
        cohort = all_cohorts_owned_by(asc_advisor_uid)[-1]
        cohort_id = cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert cohort['name'] == 'Undeclared students'
        students = cohort['students']
        assert cohort['totalStudentCount'] == len(students) == 1
        # We expect the student with 'Letters & Sci Undeclared UG' major
        assert students[0]['sid'] == '5678901234'

    def test_includes_cohort_member_sis_data(self, asc_advisor_login, asc_owned_cohort, client):
        """Includes SIS data for custom cohort students."""
        cohort_id = asc_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert athlete['cumulativeGPA'] == 3.8
        assert athlete['cumulativeUnits'] == 101.3
        assert athlete['level'] == 'Junior'
        assert athlete['majors'] == ['English BA', 'Nuclear Engineering BS']

    def test_includes_cohort_member_current_enrollments(self, asc_advisor_login, asc_owned_cohort, client):
        """Includes current-term active enrollments for custom cohort students."""
        cohort_id = asc_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}?orderBy=firstName')
        assert response.status_code == 200
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        term = athlete['term']
        assert term['termName'] == 'Fall 2017'
        assert term['enrolledUnits'] == 12.5
        assert len(term['enrollments']) == 5
        assert term['enrollments'][0]['displayName'] == 'BURMESE 1A'
        assert len(term['enrollments'][0]['canvasSites']) == 1

    def test_includes_cohort_member_term_gpa(self, asc_advisor_login, asc_owned_cohort, client):
        cohort_id = asc_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}?orderBy=firstName')
        assert response.status_code == 200
        deborah = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert len(deborah['termGpa']) == 4
        assert deborah['termGpa'][0] == {'termName': 'Spring 2018', 'gpa': 2.9}
        assert deborah['termGpa'][3] == {'termName': 'Spring 2016', 'gpa': 3.8}

    def test_includes_cohort_member_athletics_asc(self, asc_advisor_login, asc_owned_cohort, client):
        """Includes athletic data custom cohort members for ASC advisors."""
        cohort_id = asc_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert len(athlete['athleticsProfile']['athletics']) == 2
        assert athlete['athleticsProfile']['inIntensiveCohort'] is not None
        assert athlete['athleticsProfile']['isActiveAsc'] is not None
        assert athlete['athleticsProfile']['statusAsc'] is not None
        tennis = next(membership for membership in athlete['athleticsProfile']['athletics'] if membership['groupCode'] == 'WTE')
        field_hockey = next(membership for membership in athlete['athleticsProfile']['athletics'] if membership['groupCode'] == 'WFH')
        assert tennis['groupName'] == 'Women\'s Tennis'
        assert tennis['teamCode'] == 'TNW'
        assert tennis['teamName'] == 'Women\'s Tennis'
        assert field_hockey['groupName'] == 'Women\'s Field Hockey'
        assert field_hockey['teamCode'] == 'FHW'
        assert field_hockey['teamName'] == 'Women\'s Field Hockey'

    def test_omits_cohort_member_athletics_non_asc(self, coe_advisor_login, client, coe_owned_cohort):
        """Omits athletic data for non-ASC advisors."""
        cohort_id = coe_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
        secretly_an_athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert 'athletics' not in secretly_an_athlete
        assert 'inIntensiveCohort' not in secretly_an_athlete
        assert 'isActiveAsc' not in secretly_an_athlete
        assert 'statusAsc' not in secretly_an_athlete

    def test_includes_cohort_member_athletics_advisors(self, admin_login, client, coe_owned_cohort):
        """Includes athletic data for admins."""
        cohort_id = coe_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert len(athlete['athleticsProfile']['athletics']) == 2
        assert athlete['athleticsProfile']['inIntensiveCohort'] is not None
        assert athlete['athleticsProfile']['isActiveAsc'] is not None
        assert athlete['athleticsProfile']['statusAsc'] is not None

    def test_get_cohort_404(self, client, coe_advisor_login):
        """Returns a well-formed response when no cohort found."""
        response = client.get('/api/cohort/99999999')
        assert response.status_code == 404
        assert 'No cohort found' in str(response.data)

    def test_offset_and_limit(self, asc_advisor_login, asc_owned_cohort, client):
        """Returns a well-formed response with custom cohort."""
        cohort_id = asc_owned_cohort['id']
        api_path = f'/api/cohort/{cohort_id}'
        # First, offset is zero
        response = client.get(f'{api_path}?offset={0}&limit={1}')
        assert response.status_code == 200
        data_0 = json.loads(response.data)
        assert data_0['totalStudentCount'] == 4
        assert len(data_0['students']) == 1
        # Now, offset is one
        response = client.get(f'{api_path}?offset={1}&limit={1}')
        data_1 = json.loads(response.data)
        assert len(data_1['students']) == 1
        # Verify that a different offset results in a different member
        assert data_0['students'][0]['uid'] != data_1['students'][0]['uid']

    def test_unauthorized_request_for_athletic_study_center_data(self, client, fake_auth):
        """In order to access intensive_cohort, inactive status, etc. the user must be either ASC or Admin."""
        fake_auth.login('1022796')
        data = {
            'name': 'My filtered cohort just hacked the system!',
            'filters': [
                {'key': 'isInactiveAsc', 'type': 'boolean', 'value': True},
            ],
        }
        response = client.post(
            '/api/cohort/create',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == 403

    def test_my_students_filter_me(self, client, asc_advisor_login):
        cohort = CohortFilter.create(
            uid=asc_advisor_uid,
            name='All my students',
            filter_criteria={
                'cohortOwnerAcademicPlans': ['*'],
            },
        )
        response = client.get(f"/api/cohort/{cohort['id']}").json
        sids = sorted([s['sid'] for s in response['students']])
        assert sids == ['11667051', '2345678901', '3456789012', '5678901234', '7890123456', '9100000000']

    def test_my_students_filter_not_me(self, client, admin_login):
        cohort = CohortFilter.create(
            uid=asc_advisor_uid,
            name='All my students',
            filter_criteria={
                'cohortOwnerAcademicPlans': ['*'],
            },
        )
        response = client.get(f"/api/cohort/{cohort['id']}").json
        sids = sorted([s['sid'] for s in response['students']])
        assert sids == ['11667051', '2345678901', '3456789012', '5678901234', '7890123456', '9100000000']


class TestCohortCreate:
    """Cohort Create API."""

    @classmethod
    def _post_cohort_create(cls, client, json_data=(), expected_status_code=200):
        response = client.post(
            '/api/cohort/create',
            data=json.dumps(json_data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    @staticmethod
    def _api_cohort(client, cohort_id, expected_status_code=200):
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == expected_status_code
        return response.json

    def test_create_cohort(self, client, asc_advisor_login):
        """Creates custom cohort, owned by current user."""
        data = {
            'name': 'Tennis',
            'filters': [
                {'key': 'majors', 'type': 'array', 'value': 'Letters & Sci Undeclared UG'},
                {'key': 'groupCodes', 'type': 'array', 'value': 'MTE'},
                {'key': 'majors', 'type': 'array', 'value': 'English BA'},
                {'key': 'genders', 'type': 'array', 'value': 'Male'},
            ],
        }

        def _verify(api_json):
            assert api_json.get('name') == 'Tennis'
            assert api_json['alertCount'] is not None
            assert len(api_json.get('criteria', {}).get('majors')) == 2
            # ASC specific
            team_groups = api_json.get('teamGroups')
            assert len(team_groups) == 1
            assert team_groups[0].get('groupCode') == 'MTE'
            # Students
            students = api_json.get('students')
            assert len(students) == 1
            assert students[0]['gender'] == 'Male'
            assert students[0]['minority'] is False

        data = self._post_cohort_create(client, data)
        _verify(data)
        cohort_id = data.get('id')
        assert cohort_id
        _verify(self._api_cohort(client, cohort_id))

    def test_asc_advisor_is_forbidden(self, asc_advisor_login, client, fake_auth):
        """Denies ASC advisor access to COE data."""
        data = {
            'name': 'ASC advisor wants to see students of COE advisor',
            'filters': [
                {
                    'key': 'coeEthnicities',
                    'type': 'array',
                    'value': 'Vietnamese',
                },
            ],
        }
        assert self._post_cohort_create(client, data, expected_status_code=403)

    def test_admin_create_of_coe_uid_cohort(self, admin_login, client, fake_auth):
        """Allows Admin to access COE data."""
        data = {
            'name': 'Admin wants to see students of COE advisor',
            'filters': [
                {
                    'key': 'coeGenders',
                    'type': 'array',
                    'value': 'M',
                },
                {
                    'key': 'genders',
                    'type': 'array',
                    'value': 'Different Identity',
                },
            ],
        }
        api_json = self._post_cohort_create(client, data)
        assert len(api_json['students']) == 2
        for student in api_json['students']:
            assert student['gender'] == 'Different Identity'
            assert student['coeProfile']['gender'] == 'M'

    def test_create_complex_cohort(self, client, coe_advisor_login):
        """Creates custom cohort, with many non-empty filter_criteria."""
        data = {
            'name': 'Complex',
            'filters': [
                {'key': 'majors', 'type': 'array', 'value': 'Gender and Women''s Studies'},
                {'key': 'gpaRanges', 'type': 'array', 'value': 'numrange(2, 2.5, \'[)\')'},
                {'key': 'levels', 'type': 'array', 'value': 'Junior'},
                {'key': 'coeGenders', 'type': 'array', 'value': 'M'},
                {'key': 'genders', 'type': 'array', 'value': 'Genderqueer/Gender Non-Conform'},
                {'key': 'gpaRanges', 'type': 'array', 'value': 'numrange(0, 2, \'[)\')'},
                {'key': 'majors', 'type': 'array', 'value': 'Environmental Economics & Policy'},
            ],
        }
        api_json = self._post_cohort_create(client, data)
        cohort_id = api_json['id']
        api_json = self._api_cohort(client, cohort_id)
        assert api_json['alertCount'] is not None
        criteria = api_json.get('criteria')
        # Genders
        assert criteria.get('genders') == ['Genderqueer/Gender Non-Conform']
        # COE genders
        assert criteria.get('coeGenders') == ['M']
        # GPA
        gpa_ranges = criteria.get('gpaRanges')
        assert len(gpa_ranges) == 2
        assert 'numrange(0, 2, \'[)\')' in gpa_ranges
        # Levels
        assert criteria.get('levels') == ['Junior']
        # Majors
        majors = criteria.get('majors')
        assert len(majors) == 2
        assert 'Gender and Women''s Studies' in majors

    def test_admin_creation_of_asc_cohort(self, client, admin_login):
        """COE advisor cannot use ASC criteria."""
        self._post_cohort_create(
            client,
            {
                'name': 'Admin superpowers',
                'filters': [
                    {'key': 'groupCodes', 'type': 'array', 'value': 'MTE'},
                    {'key': 'groupCodes', 'type': 'array', 'value': 'WWP'},
                ],
            },
        )

    def test_forbidden_cohort_creation(self, client, coe_advisor_login):
        """COE advisor cannot use ASC criteria."""
        data = {
            'name': 'Sorry Charlie',
            'filters': [
                {'key': 'groupCodes', 'type': 'array', 'value': 'MTE'},
            ],
        }
        self._post_cohort_create(client, data, expected_status_code=403)


class TestCohortUpdate:
    """Cohort Update API."""

    @classmethod
    def _post_cohort_update(cls, client, json_data=()):
        return client.post(
            '/api/cohort/update',
            data=json.dumps(json_data),
            content_type='application/json',
        )

    def test_unauthorized_cohort_update(self, client, coe_advisor_login):
        cohort = CohortFilter.create(
            uid=asc_advisor_uid,
            name='Swimming, Men\'s',
            filter_criteria={
                'groupCodes': ['MSW', 'MSW-DV', 'MSW-SW'],
            },
        )
        data = {
            'id': cohort['id'],
            'name': 'Hack the name!',
        }
        response = self._post_cohort_update(client, data)
        assert 403 == response.status_code

    def test_update_filters(self, client, asc_advisor_login):
        cohort = CohortFilter.create(
            uid=asc_advisor_uid,
            name='Swimming, Men\'s',
            filter_criteria={
                'groupCodes': ['MSW', 'MSW-DV', 'MSW-SW'],
            },
        )
        # First, we POST an empty name
        cohort_id = cohort['id']
        response = self._post_cohort_update(client, {'id': cohort_id})
        assert 400 == response.status_code
        # Now, we POST a valid name
        data = {
            'id': cohort_id,
            'filters': [
                {'key': 'majors', 'type': 'array', 'value': 'Gender and Women''s Studies'},
                {'key': 'gpaRanges', 'type': 'array', 'value': 'numrange(2, 2.5, \'[)\')'},
            ],
        }
        response = self._post_cohort_update(client, data)
        assert 200 == response.status_code
        updated_cohort = response.json
        assert updated_cohort['alertCount'] is not None
        assert updated_cohort['criteria']['majors'] == ['Gender and Women''s Studies']
        assert updated_cohort['criteria']['gpaRanges'] == ['numrange(2, 2.5, \'[)\')']
        assert updated_cohort['criteria']['groupCodes'] is None

        def remove_empties(criteria):
            return {k: v for k, v in criteria.items() if v is not None}
        cohort = CohortFilter.find_by_id(cohort_id)
        expected = remove_empties(cohort['criteria'])
        actual = remove_empties(updated_cohort['criteria'])
        assert expected == actual

    def test_cohort_update_filter_criteria(self, client, asc_advisor_login):
        name = 'Swimming, Men\'s'
        cohort = CohortFilter.create(
            uid=asc_advisor_uid,
            name=name,
            filter_criteria={
                'groupCodes': ['MBB'],
            },
        )
        cohort_id = cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        cohort = json.loads(response.data)
        assert cohort['totalStudentCount'] == 1
        # Update the db
        updates = {
            'id': cohort_id,
            'criteria': {
                'groupCodes': ['MBB', 'MBB-AA'],
            },
        }
        response = self._post_cohort_update(client, updates)
        assert response.status_code == 200
        # Verify the value of 'student_count' in db
        updated_cohort = CohortFilter.find_by_id(cohort_id)
        assert updated_cohort['totalStudentCount'] == 2
        assert 'sids' not in updated_cohort
        assert updated_cohort['criteria']['groupCodes'] == updates['criteria']['groupCodes']


class TestCohortDelete:
    """Cohort Delete API."""

    def test_delete_cohort_not_authenticated(self, client):
        """Custom cohort deletion requires authentication."""
        response = client.delete('/api/cohort/delete/123')
        assert response.status_code == 401

    def test_delete_cohort_wrong_user(self, client, fake_auth):
        """Custom cohort deletion is only available to owners."""
        cohort = CohortFilter.create(
            uid=coe_advisor_uid,
            name='Badminton teams',
            filter_criteria={
                'groupCodes': ['WWP', 'MWP'],
            },
        )
        assert cohort

        # This user does not own the custom cohort above
        fake_auth.login('2040')
        cohort_id = cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
        _cohort = json.loads(response.data)
        assert _cohort['isOwnedByCurrentUser'] is False

        response = client.delete(f'/api/cohort/delete/{cohort_id}')
        assert response.status_code == 400
        assert '2040 does not own' in str(response.data)

    def test_delete_cohort(self, client, coe_advisor_login):
        """Deletes existing custom cohort while enforcing rules of ownership."""
        name = 'Water polo teams'
        cohort = CohortFilter.create(
            uid=coe_advisor_uid,
            name=name,
            filter_criteria={
                'groupCodes': ['WWP', 'MWP'],
            },
        )
        # Verify deletion
        cohort_id = cohort['id']
        response = client.delete(f'/api/cohort/delete/{cohort_id}')
        assert response.status_code == 200
        cohorts = all_cohorts_owned_by(asc_advisor_uid)
        assert not next((c for c in cohorts if c['id'] == cohort_id), None)


class TestCohortPerFilters:
    """Cohort API."""

    @classmethod
    def _api_get_students_per_filters(cls, client, json_data=(), expected_status_code=200):
        response = client.post(
            '/api/cohort/get_students_per_filters',
            data=json.dumps(json_data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_students_per_filters_not_authenticated(self, client):
        """API requires authentication."""
        self._api_get_students_per_filters(client, expected_status_code=401)

    def test_students_per_filters_with_empty(self, client, coe_advisor_login):
        """API requires non-empty input."""
        self._api_get_students_per_filters(client, {'filters': []}, expected_status_code=400)

    def test_students_per_filters_unauthorized(self, client, asc_advisor_login):
        """ASC advisor is not allowed to query with COE attributes."""
        self._api_get_students_per_filters(
            client,
            {
                'filters':
                    [
                        {
                            'key': 'coeProbation',
                            'type': 'boolean',
                            'value': 'true',
                        },
                    ],
            },
            expected_status_code=403,
        )

    def test_students_per_filters_coe_advisor(self, client, coe_advisor_login):
        """API translates 'coeProbation' filter to proper filter_criteria query."""
        gpa_range_1 = 'numrange(0, 2, \'[)\')'
        gpa_range_2 = 'numrange(2, 2.5, \'[)\')'
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters':
                    [
                        {
                            'key': 'coeProbation',
                            'type': 'boolean',
                            'value': 'true',
                        },
                        {
                            'key': 'gpaRanges',
                            'type': 'array',
                            'value': gpa_range_1,
                        },
                        {
                            'key': 'gpaRanges',
                            'type': 'array',
                            'value': gpa_range_2,
                        },
                        {
                            'key': 'lastNameRange',
                            'type': 'range',
                            'value': ['A', 'Z'],
                        },
                    ],
            },
        )
        assert 'totalStudentCount' in api_json
        assert 'students' in api_json
        criteria = api_json['criteria']
        assert criteria['coeProbation'] is not None
        assert criteria['lastNameRange'] is not None
        gpa_ranges = criteria['gpaRanges']
        assert len(gpa_ranges) == 2
        assert gpa_range_1 in gpa_ranges
        assert gpa_range_2 in gpa_ranges
        for key in [
            'coeAdvisorLdapUids',
            'coeEthnicities',
            'ethnicities',
            'expectedGradTerms',
            'genders',
            'groupCodes',
            'inIntensiveCohort',
            'isInactiveAsc',
            'levels',
            'majors',
            'transfer',
            'underrepresented',
            'unitRanges',
        ]:
            assert criteria[key] is None

    def test_my_students_filter_all_plans(self, client, coe_advisor_login):
        """Returns students mapped to advisor, across all academic plans."""
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {
                        'key': 'cohortOwnerAcademicPlans',
                        'type': 'array',
                        'value': '*',
                    },
                ],
            },
        )
        sids = sorted([s['sid'] for s in api_json['students']])
        assert sids == ['11667051', '7890123456', '9000000000', '9100000000']

    def test_my_students_filter_selected_plans(self, client, coe_advisor_login):
        """Returns students mapped to advisor, per specified academic plans."""
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {
                        'key': 'cohortOwnerAcademicPlans',
                        'type': 'array',
                        'value': '162B0U',
                    },
                    {
                        'key': 'cohortOwnerAcademicPlans',
                        'type': 'array',
                        'value': '162B3U',
                    },
                ],
            },
        )
        sids = sorted([s['sid'] for s in api_json['students']])
        assert sids == ['7890123456', '9000000000']

    def _get_defensive_line(self, client, inactive_asc, order_by):
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters':
                    [
                        {
                            'key': 'groupCodes',
                            'type': 'array',
                            'value': 'MFB-DL',
                        },
                        {
                            'key': 'isInactiveAsc',
                            'type': 'boolean',
                            'value': inactive_asc,
                        },
                    ],
                'orderBy': order_by,
            },
        )
        return api_json['students']

    def test_students_per_filters_order_by(self, client, asc_advisor_login):
        """Returns properly ordered list of students."""
        def _get_first_student(order_by):
            students = self._get_defensive_line(client, False, order_by)
            assert len(students) == 3
            return students[0]
        assert _get_first_student('first_name')['firstName'] == 'Dave'
        assert _get_first_student('last_name')['lastName'] == 'Doolittle'
        assert _get_first_student('gpa')['cumulativeGPA'] == 3.005
        assert _get_first_student('level')['level'] == 'Junior'
        assert _get_first_student('major')['majors'][0] == 'Chemistry BS'
        assert _get_first_student('units')['cumulativeUnits'] == 34
        student = _get_first_student('group_name')
        assert student['athleticsProfile']['athletics'][0]['groupName'] == 'Football, Defensive Backs'

    def test_student_athletes_inactive_asc(self, client, asc_advisor_login):
        """An ASC advisor query defaults to active athletes only."""
        students = self._get_defensive_line(client, False, 'gpa')
        assert len(students) == 3
        for student in students:
            assert student['athleticsProfile']['isActiveAsc'] is True

    def test_student_athletes_inactive_admin(self, client, admin_login):
        """An admin query defaults to active and inactive athletes."""
        students = self._get_defensive_line(client, None, 'gpa')
        assert len(students) == 4

        def is_active_asc(student):
            return student['athleticsProfile']['isActiveAsc']
        assert is_active_asc(students[0]) is False
        assert is_active_asc(students[1]) is True
        assert is_active_asc(students[2]) is True
        assert is_active_asc(students[3]) is True

    def test_filter_expected_grad_term(self, client, coe_advisor_login):
        """Returns students per expected graduation."""
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters':
                    [
                        {
                            'key': 'expectedGradTerms',
                            'type': 'array',
                            'value': '2202',
                        },
                    ],
            },
        )
        students = api_json['students']
        assert len(students) == 2
        for student in students:
            assert student['expectedGraduationTerm']['name'] == 'Spring 2020'

    def test_filter_transfer(self, client, coe_advisor_login):
        """Returns list of transfer students."""
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters':
                    [
                        {
                            'key': 'transfer',
                            'type': 'boolean',
                            'value': True,
                        },
                    ],
            },
        )
        students = api_json['students']
        assert len(students) == 2
        for student in students:
            assert student['transfer'] is True

    def test_ethnicities_filter(self, client, coe_advisor_login):
        """Returns students of specified ethnicity."""
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {
                        'key': 'ethnicities',
                        'type': 'array',
                        'value': 'African-American / Black',
                    },
                ],
            },
        )
        sids = sorted([s['sid'] for s in api_json['students']])
        assert sids == ['2345678901', '3456789012', '890127492']


class TestDownloadCsvPerFilters:
    """Download Cohort CSV API."""

    @classmethod
    def _api_download_csv_per_filters(cls, client, json_data=(), expected_status_code=200):
        response = client.post(
            '/api/cohort/download_csv_per_filters',
            data=json.dumps(json_data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_download_csv_not_authenticated(self, client):
        """API requires authentication."""
        self._api_download_csv_per_filters(client, expected_status_code=401)

    def test_download_csv_with_empty(self, client, coe_advisor_login):
        """API requires non-empty input."""
        self._api_download_csv_per_filters(client, {'filters': ()}, expected_status_code=400)

    def test_download_csv_unauthorized(self, client, asc_advisor_login):
        """ASC advisor is not allowed to query with COE attributes."""
        self._api_download_csv_per_filters(
            client,
            {
                'filters':
                    [
                        {
                            'key': 'coeProbation',
                            'type': 'boolean',
                            'value': 'true',
                        },
                    ],
            },
            expected_status_code=403,
        )

    def test_download_csv(self, client, coe_advisor_login):
        """Advisor can download CSV with ALL students of cohort."""
        data = {
            'filters':
                [
                    {
                        'key': 'coeEthnicities',
                        'type': 'array',
                        'value': ['H', 'B'],
                    },
                ],
        }
        response = client.post(
            '/api/cohort/download_csv_per_filters',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert 'csv' in response.content_type
        csv = str(response.data)
        for snippet in [
            'first_name,last_name,sid,email,phone',
            'Deborah,Davies,11667051,oski@berkeley.edu,415/123-4567',
            'Paul,Farestveit,7890123456,,415/123-4567',
            'Wolfgang,Pauli-O\'Rourke,9000000000,,415/123-4567',
        ]:
            assert str(snippet) in csv


class TestAllCohortFilterOptions:
    """Cohort Filter Options API."""

    @classmethod
    def _api_cohort_filter_options(cls, client, json_data=(), owner='me', expected_status_code=200):
        response = client.post(
            f'/api/cohort/filter_options/{owner}',
            data=json.dumps(json_data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    @classmethod
    def _level_option(cls, student_class_level):
        return {
            'key': 'levels',
            'type': 'array',
            'value': student_class_level,
        }

    def test_filter_options_api_not_authenticated(self, client):
        """Menu API cohort-filter-options requires authentication."""
        self._api_cohort_filter_options(client, expected_status_code=401)

    def test_filter_options_with_nothing_disabled(self, client, coe_advisor_login):
        """Menu API with all menu options available."""
        api_json = self._api_cohort_filter_options(
            client,
            {
                'existingFilters': [],
            },
        )
        for category in api_json:
            for menu in category:
                assert 'disabled' not in menu
                if menu['type'] == 'array':
                    for option in menu['options']:
                        assert 'disabled' not in option

    def test_filter_options_my_students_for_me(self, client, coe_advisor_login):
        """Returns user's own academic plans under 'My Students'."""
        api_json = self._api_cohort_filter_options(
            client,
            {
                'existingFilters': [],
            },
        )
        my_students = next(option for group in api_json for option in group if option['name'] == 'My Students')
        assert len(my_students['options']) == 5
        assert {'name': 'All plans', 'value': '*'} in my_students['options']
        assert {'name': 'Bioengineering BS', 'value': '16288U'} in my_students['options']
        assert {'name': 'Engineering Undeclared UG', 'value': '162B0U'} in my_students['options']
        assert {'name': 'BioE/MSE Joint Major BS', 'value': '162B3U'} in my_students['options']
        assert {'name': 'Bioengineering UG', 'value': '16I010U'} in my_students['options']

    def test_filter_options_my_students_for_not_me(self, client, coe_advisor_login):
        """Returns another user's academic plans under 'My Students'."""
        api_json = self._api_cohort_filter_options(
            client,
            {
                'existingFilters': [],
            },
            asc_advisor_uid,
        )
        my_students = next(option for group in api_json for option in group if option['name'] == 'My Students')
        assert len(my_students['options']) == 4
        assert {'name': 'All plans', 'value': '*'} in my_students['options']
        assert {'name': 'English BA', 'value': '25345U'} in my_students['options']
        assert {'name': 'English UG', 'value': '25I039U'} in my_students['options']
        assert {'name': 'Medieval Studies UG', 'value': '25I054U'} in my_students['options']

    def test_filter_options_with_category_disabled(self, client, coe_advisor_login):
        """The coe_probation option is disabled if it is in existing-filters."""
        api_json = self._api_cohort_filter_options(
            client,
            {
                'existingFilters':
                    [
                        {
                            'key': 'coeProbation',
                            'type': 'boolean',
                        },
                    ],
            },
        )
        assert len(api_json) == 3
        for category in api_json:
            for menu in category:
                if menu['key'] == 'coeProbation':
                    assert menu['disabled'] is True
                else:
                    assert 'disabled' not in menu

    def test_filter_options_with_one_disabled(self, client, coe_advisor_login):
        """The 'Freshman' sub-menu option is disabled if it is already in cohort filter set."""
        api_json = self._api_cohort_filter_options(
            client,
            {
                'existingFilters':
                    [
                        self._level_option('Freshman'),
                        self._level_option('Sophomore'),
                        self._level_option('Junior'),
                        {
                            'key': 'coeAdvisorLdapUids',
                            'type': 'array',
                            'value': '1022796',
                        },
                    ],
            },
        )
        assert len(api_json) == 3
        assertion_count = 0
        for category in api_json:
            for menu in category:
                # All top-level category menus are enabled
                assert 'disabled' not in menu
                if menu['key'] == 'levels':
                    for option in menu['options']:
                        disabled = option.get('disabled')
                        if option['value'] in ['Freshman', 'Sophomore', 'Junior']:
                            assert disabled is True
                            assertion_count += 1
                        else:
                            assert disabled is None
                else:
                    assert 'disabled' not in menu
        assert assertion_count == 3

    def test_all_options_in_category_disabled(self, client, coe_advisor_login):
        """Disable the category if all its options are in existing-filters."""
        api_json = self._api_cohort_filter_options(
            client,
            {
                'existingFilters':
                    [
                        self._level_option('Senior'),
                        self._level_option('Junior'),
                        self._level_option('Sophomore'),
                        self._level_option('Freshman'),
                    ],
            },
        )
        for category in api_json:
            for menu in category:
                if menu['key'] == 'levels':
                    assert menu.get('disabled') is True
                    for option in menu['options']:
                        assert option.get('disabled') is True
                else:
                    assert 'disabled' not in menu

    def test_disable_last_name_range(self, client, coe_advisor_login):
        """Disable the category if all its options are in existing-filters."""
        api_json = self._api_cohort_filter_options(
            client,
            {
                'existingFilters':
                    [
                        {
                            'key': 'lastNameRange',
                            'type': 'range',
                            'value': ['A', 'B'],
                        },
                    ],
            },
        )
        for category in api_json:
            for menu in category:
                is_disabled = menu.get('disabled')
                if menu['key'] == 'lastNameRange':
                    assert is_disabled is True
                else:
                    assert is_disabled is None


class TestTranslateToFilterOptions:
    """Cohort Filter Options API."""

    @classmethod
    def _api_translate_to_filter_options(cls, client, json_data=(), owner='me', expected_status_code=200):
        response = client.post(
            f'/api/cohort/translate_to_filter_options/{owner}',
            data=json.dumps(json_data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_translate_criteria_when_empty(self, client, coe_advisor_login):
        """Empty criteria translates to zero rows."""
        assert [] == self._api_translate_to_filter_options(
            client,
            {
                'criteria': {},
            },
        )

    def test_translate_criteria_with_boolean(self, client, coe_advisor_login):
        """Filter-criteria with boolean is properly translated."""
        json_data = {
            'criteria': {
                'isInactiveCoe': False,
            },
        }
        api_json = self._api_translate_to_filter_options(client, json_data)
        assert len(api_json) == 1
        assert api_json[0]['name'] == 'Inactive'
        assert api_json[0]['key'] == 'isInactiveCoe'
        assert api_json[0]['value'] is False

    def test_translate_criteria_with_array(self, client, coe_advisor_login):
        """Filter-criteria with array is properly translated."""
        api_json = self._api_translate_to_filter_options(
            client,
            {
                'criteria': {
                    'genders': ['Female', 'Decline to State'],
                    'levels': ['Freshman', 'Sophomore'],
                },
            },
        )
        assert len(api_json) == 4
        # Levels
        assert api_json[0]['name'] == api_json[1]['name'] == 'Level'
        assert api_json[0]['key'] == api_json[1]['key'] == 'levels'
        assert api_json[0]['value'] == 'Freshman'
        assert api_json[1]['value'] == 'Sophomore'
        # Genders
        assert api_json[2]['name'] == api_json[3]['name'] == 'Gender'
        assert api_json[2]['key'] == api_json[3]['key'] == 'genders'
        assert api_json[2]['value'] == 'Female'
        assert api_json[3]['value'] == 'Decline to State'

    def test_translate_criteria_with_range(self, client, coe_advisor_login):
        """Filter-criteria with range is properly translated."""
        api_json = self._api_translate_to_filter_options(
            client,
            {
                'criteria': {
                    'lastNameRange': ['M', 'Z'],
                },
            },
        )
        assert len(api_json) == 1
        assert api_json[0]['name'] == 'Last Name'
        assert api_json[0]['key'] == 'lastNameRange'
        assert api_json[0]['value'] == ['M', 'Z']

    def test_translate_criteria_my_students_for_me(self, client, coe_advisor_login):
        """User's own 'My Students' criteria are properly translated."""
        api_json = self._api_translate_to_filter_options(
            client,
            {
                'criteria': {
                    'cohortOwnerAcademicPlans': ['*'],
                },
            },
        )
        assert len(api_json) == 1
        assert api_json[0]['name'] == 'My Students'
        assert api_json[0]['subcategoryHeader'] == 'Choose academic plan...'
        assert api_json[0]['key'] == 'cohortOwnerAcademicPlans'
        assert api_json[0]['value'] == '*'

    def test_translate_criteria_my_students_for_not_me(self, client, coe_advisor_login):
        """Another user's 'My Students' criteria are properly translated."""
        api_json = self._api_translate_to_filter_options(
            client,
            {
                'criteria': {
                    'cohortOwnerAcademicPlans': ['25I039U', '25I054U'],
                },
            },
            asc_advisor_uid,
        )
        assert len(api_json) == 2
        assert api_json[0]['name'] == 'My Students'
        assert api_json[0]['key'] == 'cohortOwnerAcademicPlans'
        assert api_json[0]['value'] == '25I039U'
        assert api_json[1]['name'] == 'My Students'
        assert api_json[1]['key'] == 'cohortOwnerAcademicPlans'
        assert api_json[1]['value'] == '25I054U'
