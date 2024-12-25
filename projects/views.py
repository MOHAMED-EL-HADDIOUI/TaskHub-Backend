from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from projects.models import Project
from tasks.decorators import role_required
from tasks.serializers import ProjectSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project(request):
    data = request.data
    project = Project.objects.create(
        name=data['name'],
        description=data.get('description', ''),
        manager=request.user
    )
    return Response({"message": "Project created successfully.", "project_id": project.id}, status=201)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def project_list(request):
    if request.method == 'GET':
        projects = Project.objects.filter(manager=request.user)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        if request.user.role.role != 'MANAGER':
            return Response({"error": "You are not authorized to create a project."}, status=403)
        data = request.data
        data['manager'] = request.user.id
        serializer = ProjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])

def update_project(request, project_id):

    try:
        project = Project.objects.get(id=project_id, manager=request.user)
    except Project.DoesNotExist:
        return Response({"error": "Project not found or you do not have permission to edit it."}, status=404)

    serializer = ProjectSerializer(project, data=request.data, partial=True)  # Allow partial updates
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Project updated successfully.", "project": serializer.data}, status=200)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])

def delete_project(request, project_id):

    try:
        project = Project.objects.get(id=project_id, manager=request.user)
    except Project.DoesNotExist:
        return Response({"error": "Project not found or you do not have permission to delete it."}, status=404)

    project.delete()
    return Response({"message": "Project deleted successfully."}, status=204)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project_details(request, project_id):
    try:
        # Récupérer le projet par ID
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        # Retourner une erreur si le projet n'existe pas
        return Response({"error": "Project not found"}, status=404)

    # Sérialiser le projet et le retourner en réponse
    serializer = ProjectSerializer(project)
    return Response(serializer.data, status=200)