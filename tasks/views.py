from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from tasks.serializers import TaskSerializer, UserSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Project, User, Task
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # Ensures that the user is authenticated

    def get(self, request):
        user = request.user  # Access the authenticated user
        return Response({
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined
            # 'role': user.role
        })

class UserListView(APIView):
    permission_classes = [IsAuthenticated]  # Ensures that the user is authenticated
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_tasks_assigned_to_user(request):
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    tasks = Task.objects.filter(assigned_to=user)
    if not tasks:
        return Response({"message": "No tasks found for this user."}, status=status.HTTP_404_NOT_FOUND)

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_task(request, project_id):
    data = request.data
    print(request.data)

    # Validate if 'assignedTo' is provided in the request data
    assigned_to = data.get('assignedTo')
    if not assigned_to:
        return Response({"error": "Assigned user is required."}, status=400)

    # Get the project or return 404 if not found
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({"error": "Project not found."}, status=404)

    # Get the user from the 'assignedTo' field
    try:
        id_user = int(assigned_to)
        user = User.objects.get(id=id_user)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)

    # Create the task
    task = Task.objects.create(
        title=data['title'],
        description=data.get('description', ''),
        project=project,
        assigned_to=user,
        status=data.get('status', 'not-started'),
        completed=data.get('completed', False)
    )

    return Response({"message": "Task created successfully.", "task_id": task.id}, status=201)

@permission_classes([IsAuthenticated])
@api_view(['GET', 'POST'])
def task_list(request, project_id):

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({"error": "Project not found."}, status=404)

    if request.method == 'GET':
        tasks = project.tasks.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if request.user.role.role != 'MANAGER':
            return Response({"error": "You are not authorized to create a task."}, status=403)
        data = request.data
        data['project'] = project.id
        data['assigned_to'] = request.user.id  # Optionally set the manager as the assigned user
        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@permission_classes([IsAuthenticated])
@api_view(['PUT', 'PATCH'])
def update_task(request, task_id):
    data = request.data  # Extract data from request

    try:
        # Retrieve the task or return a 404 error if not found or not authorized
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({"error": "Task not found or you do not have permission to edit it."}, status=404)

    # Update task fields directly using data from request
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'assignedTo' in data:
        try:
            assigned_user = User.objects.get(id=int(data['assignedTo']))
            task.assigned_to = assigned_user
        except User.DoesNotExist:
            return Response({"error": "Assigned user not found."}, status=404)
    if 'status' in data:
        task.status = data['status']
    if 'completed' in data:
        task.completed = data['completed']

    task.save()  # Save the updated task object

    return Response({"message": "Task updated successfully.", "task_id": task.id}, status=200)

@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_task(request, task_id):

    try:
        task = Task.objects.get(id=task_id, project__manager=request.user)
    except Task.DoesNotExist:
        return Response({"error": "Task not found or you do not have permission to delete it."}, status=404)

    task.delete()
    return Response({"message": "Task deleted successfully."}, status=204)

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def register_user(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    user = User.objects.create_user(username=username, password=password,email=email)

    return Response({"message": "Utilisateur enregistré avec succès.", "username": username})


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def login_user(request):

    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Debugging: Print the incoming data
    print(f"Received username: {username}, password: {password}")

    # Authenticate the user
    user = authenticate(username=username, password=password)

    # Debugging: Print the result of authentication
    print(f"User authenticated: {user}")

    if user is not None:
        # If user is authenticated, create a token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return Response({
            'access': access_token,
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def logout_user(request):

    try:
        # Get the user's token
        token = Token.objects.get(key=request.auth.key)
        # Delete the token to log the user out
        token.delete()
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return Response({"error": "Token not found or already expired."}, status=status.HTTP_400_BAD_REQUEST)