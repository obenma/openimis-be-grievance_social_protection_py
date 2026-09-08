import base64
import json
from dataclasses import dataclass
from django.utils.translation import gettext as _
from core.models import User, filter_validity
from core.test_helpers import create_test_interactive_user
from django.conf import settings
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token
from location.models import Location
from location.test_helpers import create_test_location, assign_user_districts
from rest_framework import status
from insuree.test_helpers import create_test_insuree
from location.test_helpers import create_test_location, create_test_health_facility, create_test_village
from insuree.models import Family


# from openIMIS import schema


@dataclass
class DummyContext:
    """ Just because we need a context to generate. """
    user: User


class GrievanceGQLTestCase(GraphQLTestCase):
    GRAPHQL_URL = f'/{settings.SITE_ROOT()}graphql'
    # This is required by some version of graphene but is never used. It should be set to the schema but the import
    # is shown as an error in the IDE, so leaving it as True.
    GRAPHQL_SCHEMA = True
    admin_user = None
    ca_user = None
    ca_token = None
    test_village = None
    test_insuree = None
    test_photo = None
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_village = create_test_village()
        cls.test_insuree = create_test_insuree(with_family=True, is_head=True, custom_props={'current_village':cls.test_village}, family_custom_props={'location':cls.test_village})
        cls.admin_user = create_test_interactive_user(username="testLocationAdmin")
        cls.admin_token = get_token(cls.admin_user, DummyContext(user=cls.admin_user))
        cls.ca_user = create_test_interactive_user(username="testLocationNoRight", roles=[9])
        cls.ca_token = get_token(cls.ca_user, DummyContext(user=cls.ca_user))
        cls.admin_dist_user = create_test_interactive_user(username="testLocationDist")
        assign_user_districts(cls.admin_dist_user, ["R1D1", "R2D1", "R2D2", "R2D1", cls.test_village.parent.parent.code])
        cls.admin_dist_token = get_token(cls.admin_dist_user, DummyContext(user=cls.admin_dist_user))
        cls.photo_base64 = "iVBORw0KGgoAAAANSUhEUgAAAQAAAAEAAQMAAABmvDolAAAAA1BMVEW10NBjBBbqAAAAH0lEQVRoge3BAQ0AAADCoPdPbQ43oAAAAAAAAAAAvg0hAAABmmDh1QAAAABJRU5ErkJggg=="

    def test_query_insuree_number_validity(self):
        response = self.query(
            '''

    mutation {
      createTicket(
        input: {
          clientMutationId: "55f1ee07-7ba2-49bc-a3d2-6ba057596c1e"
          clientMutationLabel: "Created Ticket Joseph Macintyre"
          insureeUuid: "0539afeb-21a1-4b3f-9478-23e6f41b0024"
          categoryUuid: "6a9a9e3c-efb3-4cc5-a5ea-7200a49ce1cc"
          dateOfIncident: "2024-03-04"
          ticketPriority: "Critical"
              }
            ) {
              clientMutationId
              internalId
            }
          }
            ''',
            headers={"HTTP_AUTHORIZATION": f"Bearer {self.admin_token}"},
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        


