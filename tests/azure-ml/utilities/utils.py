from azure.ml._workspace_dependent_operations import WorkspaceScope


def write_script(script_path: str, content: str) -> str:
    """
    Util for generating a python script, currently writes the file to disk.
    """
    with open(script_path, "w") as stream:
        stream.write(content)
    return script_path


def get_arm_id(
        ws_scope: WorkspaceScope,
        entity_name: str,
        entity_version: str,
        entity_type) -> str:
    arm_id = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{" \
             "}/{}/{}/versions/{}" \
        .format(
            ws_scope.subscription_id,
            ws_scope.resource_group_name,
            ws_scope.workspace_name,
            entity_type,
            entity_name,
            entity_version)

    return arm_id
