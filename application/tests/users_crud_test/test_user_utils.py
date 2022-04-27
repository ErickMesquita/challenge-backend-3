import pytest
from application.controller import user_utils as u_utils
from application.models.user import User
from application.controller.user_utils.user_creation_strategies import CreateNewUserStrategy, \
	ReactivateUserStrategy, DontCreateUserStrategy
from application.controller.user_utils.user_edit_strategies import UserEditStrategy, SameUsernameStrategy, \
	NewAvailableUsernameStrategy, InactiveUsernameStrategy, DontEditUserStrategy


@pytest.fixture
def conflicting_users_list():
	user_test = User(username="test", email="test@example.com", active=True)
	user_test2 = User(username="test2", email="test2@example.com", active=False)
	user_test3 = User(username="test3", email="test3@example.com", active=True)

	return [user_test, user_test2, user_test3]


@pytest.mark.parametrize(('conflicts_list', 'result'), (
		(["OK", "OK", "OK", "OK"], CreateNewUserStrategy),
		(["Forbidden", "Reactivate", "OK", "Forbidden"], DontCreateUserStrategy),
		(["Reactivate", "OK", "OK", "OK"], ReactivateUserStrategy),
		(["Reactivate", "OK", "Reactivate", "OK"], ReactivateUserStrategy)
))
def test_creation_strategy_from_conflicts_list(conflicts_list, result):
	assert u_utils.get_creation_strategy_from_conflicts_list(conflicts_list) == result


@pytest.mark.parametrize(('conflicts_list', 'new_username', 'current_username', 'result'), (
		(["OK", "OK", "OK"], "equal", "equal", SameUsernameStrategy),
		(["OK", "OK", "OK"], "diff1", "diff2", NewAvailableUsernameStrategy),
		(["Forbidden", "Reactivate", "OK"], "equal", "equal", SameUsernameStrategy),
		(["Forbidden", "Reactivate", "OK"], "diff1", "diff2", DontEditUserStrategy),
		(["Reactivate", "OK", "OK"], "equal", "equal", SameUsernameStrategy),
		(["Reactivate", "OK", "OK"], "diff1", "diff2", InactiveUsernameStrategy)
))
def test_edit_strategy_from_conflicts_list(conflicts_list, new_username, current_username, result):
	assert u_utils.get_edit_strategy_from_conflicting_users_list(conflicts_list, new_username, current_username) == result


def test_conflicts_list_from_users_list(conflicting_users_list):
	new_usernames_list = ["test", "test2", "test3"]

	expected_results_list = [
		["Forbidden", "OK", "Forbidden"],
		["Forbidden", "Reactivate", "Forbidden"],
		["Forbidden", "OK", "Forbidden"],
	]

	for new_username, expected_result in zip(new_usernames_list, expected_results_list):
		assert u_utils.conflicts_list_from_users_list(conflicting_users_list=conflicting_users_list,
													  new_username=new_username) == expected_result
