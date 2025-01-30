import json
from django.views import View
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateparse import parse_date
from ufcmsdb.models import Project, CustomUser
from rest_framework.views import APIView

class CreateProjectView(APIView):
    authentication_classes = [TokenAuthentication]  # Require token authentication
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        try:
            # Get the user from the token
            user = request.user

            # Parse JSON payload
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

            # Extract required fields
            name = data.get('name')
            deadline = data.get('deadline')
            leader_id = data.get('leader')
            description = data.get('description', '')

            # Validate required fields
            if not name or not deadline or not leader_id:
                return JsonResponse({'error': 'Name, deadline, and leader are required.'}, status=400)

            # Parse deadline to date
            parsed_deadline = parse_date(deadline)
            if not parsed_deadline:
                return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

            # Validate leader
            try:
                leader = CustomUser.objects.get(id=leader_id)
            except CustomUser.DoesNotExist:
                return JsonResponse({'error': 'Leader with the provided ID does not exist.'}, status=404)

            # Create the project
            project = Project.objects.create(
                name=name,
                deadline=parsed_deadline,
                leader=leader,
                description=description,
                created_by=user  # Assign the user who created the project
            )

            # Handle optional team members
            team_members_ids = data.get('team_members', [])
            if team_members_ids:
                # Validate team members
                team_members = CustomUser.objects.filter(id__in=team_members_ids)
                if len(team_members) != len(team_members_ids):
                    return JsonResponse({'error': 'One or more team member IDs are invalid.'}, status=400)
                project.team_members.set(team_members)

            # Construct response data
            response_data = {
                'id': project.id,
                'name': project.name,
                'deadline': project.deadline,
                'leader': {
                    'id': leader.id,
                    'name': f"{leader.first_name} {leader.last_name}", 
                    'profile_pic': leader.profile_pic.url if leader.profile_pic else None
                },
                'team_members': [
                    {'id': member.id, 'name': f"{member.first_name} {member.last_name}"} for member in project.team_members.all()
                ],
                'description': project.description,
                'created_by': {
                    'id': user.id,
                    'name': f"{user.first_name} {user.last_name}"
                }
            }

            return JsonResponse({'message': 'Project created successfully.', 'project': response_data}, status=201)

        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
class GetProjectDetailsView(View):
    def get(self, request, project_id=None):
        try:
            if not project_id:
                return JsonResponse({'error': 'Project ID is required.'}, status=400)

            # Fetch the project details
            project = Project.objects.prefetch_related('team_members', 'leader').get(id=project_id)

            # Construct response data
            response_data = {
                'id': project.id,
                'name': project.name,
                'deadline': project.deadline,
                'description': project.description,
                'total_tasks': project.total_tasks,
                'created_at': project.created_at,
                'updated_at': project.updated_at,
                'leader': {
                    'id': project.leader.id,
                    'name': project.leader.name,
                    'profile_pic': project.leader.profile_pic.url if project.leader.profile_pic else None
                },
                'team_members': [
                    {
                        'id': member.id,
                        'name': f"{project.leader.first_name} {project.leader.last_name}",               
                        'profile_pic': member.profile_pic.url if member.profile_pic else None
                    }
                    for member in project.team_members.all()
                ]
            }

            return JsonResponse({'project': response_data}, status=200)

        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Project not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
class GetAllProjectsView(APIView):
    authentication_classes = [TokenAuthentication]  # Require token authentication
    permission_classes = [IsAuthenticated]  # Require the user to be authenticated

    def get(self, request):
        try:
            # Fetch all projects
            projects = Project.objects.prefetch_related('team_members', 'leader').all()

            # Construct response data
            response_data = []
            for project in projects:
                project_data = {
                    'id': project.id,
                    'name': project.name,
                    'deadline': project.deadline,
                    'description': project.description,
                    'total_tasks': project.total_tasks,
                    'created_at': project.created_at,
                    'updated_at': project.updated_at,
                    'leader': {
                        'id': project.leader.id,
                        'name': f"{project.leader.first_name} {project.leader.last_name}",               
                        'profile_pic': project.leader.profile_pic.url if project.leader.profile_pic else None
                    },
                    'team_members': [
                        {
                            'id': member.id,
                            'name': f"{member.first_name} {member.last_name}",
                            'profile_pic': member.profile_pic.url if member.profile_pic else None
                        }
                        for member in project.team_members.all()
                    ],
                    'created_by': {
                        'id': project.created_by.id,
                        'name': f"{project.created_by.first_name} {project.created_by.last_name}"
                    } if project.created_by else None
                }
                response_data.append(project_data)

            return Response({'projects': response_data}, status=200)

        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
class DeleteProjectView(APIView):
    def delete(self, request, project_id=None):
        try:
            if not project_id:
                return JsonResponse({'error': 'Project ID is required.'}, status=400)

            # Fetch and delete the project
            try:
                project = Project.objects.get(id=project_id)
                project.delete()
                return JsonResponse({'message': 'Project deleted successfully.'}, status=200)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Project not found.'}, status=404)

        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
class UpdateProjectView(APIView):
    def post(self, request, project_id=None):
        try:
            if not project_id:
                return JsonResponse({'error': 'Project ID is required.'}, status=400)

            # Parse JSON payload
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

            # Fetch the project to update
            try:
                project = Project.objects.prefetch_related('team_members', 'leader').get(id=project_id)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Project not found.'}, status=404)

            # Update project fields if provided
            if 'name' in data:
                project.name = data['name']
            if 'deadline' in data:
                parsed_deadline = parse_date(data['deadline'])
                if not parsed_deadline:
                    return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
                project.deadline = parsed_deadline
            if 'leader' in data:
                try:
                    leader = CustomUser.objects.get(id=data['leader'])
                    project.leader = leader
                except ObjectDoesNotExist:
                    return JsonResponse({'error': 'Leader with the provided ID does not exist.'}, status=404)
            if 'description' in data:
                project.description = data['description']

            # Handle optional team members
            if 'team_members' in data:
                team_members_ids = data['team_members']
                if team_members_ids:
                    team_members = CustomUser.objects.filter(id__in=team_members_ids)
                    if len(team_members) != len(team_members_ids):
                        return JsonResponse({'error': 'One or more team member IDs are invalid.'}, status=400)
                    project.team_members.set(team_members)

            # Save the updated project
            project.save()

            # Construct response data
            response_data = {
                'id': project.id,
                'name': project.name,
                'deadline': project.deadline,
                'description': project.description,
                'total_tasks': project.total_tasks,
                'created_at': project.created_at,
                'updated_at': project.updated_at,
                'leader': {
                    'id': project.leader.id,
                    'name': f"{leader.first_name} {leader.last_name}", 
                    'profile_pic': project.leader.profile_pic.url if project.leader.profile_pic else None
                },
                'team_members': [
                    {
                        'id': member.id,
                        'name': member.name,
                        'profile_pic': member.profile_pic.url if member.profile_pic else None
                    }
                    for member in project.team_members.all()
                ]
            }

            return JsonResponse({'message': 'Project updated successfully.', 'project': response_data}, status=200)

        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
