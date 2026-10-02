import json
import os
import uuid
import boto3

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])


def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }


def lambda_handler(event, context):
    method = event["requestContext"]["http"]["method"]
    student_id = (event.get("pathParameters") or {}).get("id")
    body = json.loads(event["body"]) if event.get("body") else {}

    try:
        if method == "GET" and not student_id:
            return response(200, table.scan().get("Items", []))

        if method == "GET":
            item = table.get_item(Key={"id": student_id}).get("Item")
            return response(200, item) if item else response(404, {"error": "Not found"})

        if method == "POST":
            if not body.get("name") or not body.get("email"):
                return response(400, {"error": "name and email are required"})
            item = {
                "id": str(uuid.uuid4()),
                "name": body["name"],
                "email": body["email"],
                "course": body.get("course", ""),
            }
            table.put_item(Item=item)
            return response(201, item)

        if method == "PUT" and student_id:
            item = {
                "id": student_id,
                "name": body.get("name", ""),
                "email": body.get("email", ""),
                "course": body.get("course", ""),
            }
            table.put_item(Item=item)
            return response(200, item)

        if method == "DELETE" and student_id:
            table.delete_item(Key={"id": student_id})
            return response(200, {"message": "Deleted"})

        return response(405, {"error": "Method not allowed"})

    except Exception as e:
        return response(500, {"error": str(e)})