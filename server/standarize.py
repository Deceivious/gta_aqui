from server.firewall_helper import get_rules


def standarize_users():
    list_data = get_rules()
    if not len(list_data):
        return "No users have registered."

    list_data = [
        {**i,
         **{
             "Actions":
                 "<form method='POST' action='/delete/" +
                 i["Rule Name"] + "' method='POST'><input type='submit' value='DELETE'></form>"}
         }
        for i in list_data]
    return list_data
