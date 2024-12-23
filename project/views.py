from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

def authenticate_jwt_token(request):
    auth_header = request.headers.get('Authorization', None)
    if not auth_header:
        raise AuthenticationFailed('Authorization header is expected.')

    try:
        token = auth_header.split(' ')[1]
        jwt_auth = JWTAuthentication()
        user, _ = jwt_auth.authenticate(request)  
        return user
    except IndexError:
        raise AuthenticationFailed('Token not found in Authorization header.')
    except Exception:
        raise AuthenticationFailed('Invalid or expired token.')


class ProjectListCreateView(APIView):
    def get(self, request):
        user = authenticate_jwt_token(request)
        projects = Project.objects.filter(created_by=user)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = authenticate_jwt_token(request)
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):
    def get(self, request, pk):
        user = authenticate_jwt_token(request)
        try:
            project = Project.objects.get(pk=pk, created_by=user)
            serializer = ProjectSerializer(project)
            return Response(serializer.data)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        user = authenticate_jwt_token(request)
        try:
            project = Project.objects.get(pk=pk, created_by=user)
            serializer = ProjectSerializer(project, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        user = authenticate_jwt_token(request)

        if not user.is_superuser:
            return Response({"error": "You do not have permission to delete this project."}, status=status.HTTP_403_FORBIDDEN)

        try:
            project = Project.objects.get(pk=pk, created_by=user)
            project.delete()
            return Response({"message": "Project deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)


class TaskListCreateView(APIView):
    def get(self, request):
        user = authenticate_jwt_token(request)
        tasks = Task.objects.filter(assigned_to=user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = authenticate_jwt_token(request)
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(assigned_to=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    def get(self, request, pk):
        user = authenticate_jwt_token(request)
        try:
            task = Task.objects.get(pk=pk, assigned_to=user)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        user = authenticate_jwt_token(request)
        try:
            task = Task.objects.get(pk=pk, assigned_to=user)
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        user = authenticate_jwt_token(request)
        try:
            task = Task.objects.get(pk=pk, assigned_to=user)
            task.delete()
            return Response({"message": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)


class CustomLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if username is None or password is None:
            return Response({'error': 'Please provide both username and password.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({
                'access': access_token,
                'refresh': refresh_token,
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


