from emaildjango.databasesetup import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import crypto
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from emaildjango.serializers import EmployeeSerializer
from django.utils.crypto import get_random_string
from django.core.mail import EmailMultiAlternatives




#send email to thoese emails which are in database in employee table
class send_email_to_employees(APIView):
    def get(self,request):
            with connections['default'].cursor() as cursor:
                cursor.execute("SELECT email FROM employees")
                rows = cursor.fetchall()
                try:
                    for row in rows:
                        email = row[0]
                        # Generate activation token
                        token = crypto.get_random_string(length=32)
                        # Save activation token in the database
                        cursor.execute("UPDATE employees SET activation_token = %s WHERE email = %s", [token, email])

                        # Construct activation link
                        activation_link = f"http://127.0.0.1:8000/activate/{token}"

                        subject = "Password Activation"
                        message="Activate your account"
                        message1 = f"Click the following link to activate your account: <a href='{activation_link}'>Activate Account</a>"
                        #  "Please set your password to activate your account: {activation_link} "
                        email= EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                        # send_mail(
                        #     subject,
                        #     message,
                        #     settings.DEFAULT_FROM_EMAIL,  # Use the default sender email from settings
                        #     [email],
                        #     # verify=False,  # Disable SSL certificate check
                        #     # fail_silently=True,  # Set to True to suppress exceptions, False to raise exceptions on errors
                        # )
                        email.attach_alternative(message1, "text/html")
                        email.send()
                    return Response({"message: Email sent"}, status=200)
                except Exception as e:
                    print(e)
                    return HttpResponse("Email not sent",status=400)

        
class activate_user(APIView):
    def put(self,request):
        email=request.data.get('email')
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute("UPDATE employees SET isActive=True WHERE email=%s",[email])
                connections['default'].commit()
            return Response({"message:User activated successfully"},status=200)
        except:
            return Response({"message:User not found"},status=400)
   

        
def updateDatabase(request):
    # createTable()
    insertData()
    # createSession()
    # alterTable()
   
    return HttpResponse("Database updated")
    
        

class listEmployees(APIView):
    def get(self,request,id=None):
        session_key = request.COOKIES.get('sessionid')
        if not session_key:
            return Response({"message:Please log in first"},status=400)
        else:
      
            # Query the "sessions" table using the session key to retrieve the user ID
            with connections['default'].cursor() as cursor:
                cursor.execute("SELECT user_id FROM sessions WHERE session_key = %s", [session_key])
                row = cursor.fetchone()

                if row:
                    user_id = row[0]
                    

                    # Fetch user information from the "employees" table using the user ID
                    with connections['default'].cursor() as cursor:
                        cursor.execute("SELECT id,isManager FROM employees WHERE id = %s", [user_id])
                        user_row = cursor.fetchone()
                        user_id,isManager=user_row
                        if isManager:
                            with connections['default'].cursor() as cursor:
                                if id is not None:    
                                    cursor.execute(""" SELECT * FROM employees 
                                            WHERE id=%s """,[id])
                                    rows=cursor.fetchall()
                                    if not rows:
                                        return Response({"message: Employee not found"}, status=404)
                                else:
                                    cursor.execute("""SELECT * FROM employees""")
                                    rows = cursor.fetchall()
                                columns = [col[0] for col in cursor.description]
                                data = [dict(zip(columns, row)) for row in rows]
                            serializer=EmployeeSerializer(data,many=True)
                            return Response(serializer.data, status=200)
                        else:
                            return Response({"message:You are not authorized to view this page. Can be viewed by admin only"},status=400)
                else:
                    return Response({"message:Please log in first"},status=400)
                
class addEmployee(APIView):   
    def post(self,request):
        email = request.data.get('email')
        is_manager = request.data.get('ismanager')
        age = request.data.get('age')
        with connections['default'].cursor() as cursor:
            cursor.execute("""
                INSERT INTO employees (email, isManager, age)
                VALUES (%s, %s, %s)
            """, [email, is_manager, age])
                # Commit the transaction
            connections['default'].commit()
        return Response({"message:Employee added successfully"},status=201)  
    

class deleteEmployee(APIView):    
    def delete(self,request,id):
        with connections['default'].cursor() as cursor:
           
            cursor.execute(""" 
                        DELETE FROM employees
                        WHERE id=%s""",[id])
            rows_affected = cursor.rowcount
            if rows_affected == 0:
                return Response({"message:Employee not found"},status=404)
            else:
                connections['default'].commit()
                
                return Response({"message:Employee deleted successfully"},status=200)
            
class updateEmployee(APIView):
    def put(self, request, id):
        with connections['default'].cursor() as cursor:
            update_query = "UPDATE employees SET "
            params = []
            
            if 'email' in request.data:
                update_query += "email = %s, "
                params.append(request.data['email'])
            
            if 'ismanager' in request.data:
                update_query += "isManager = %s, "
                params.append(request.data['ismanager'])
            
            if 'age' in request.data:
                update_query += "age = %s, "
                params.append(request.data['age'])
            
            # Remove the trailing comma and space from the query
            update_query = update_query.rstrip(', ')
            
            if len(params) == 0:
                return HttpResponse("No fields to update", status=400)
            
            update_query += " WHERE id = %s"
            params.append(id)
            cursor.execute(update_query, params)
            rows_affected = cursor.rowcount

            if rows_affected == 0:
                return HttpResponse("Employee does not exist", status=404)
            else:
                connections['default'].commit()
                return HttpResponse("Employee updated successfully")
               
class activate_account(APIView):
    
    def post(self,request, token):
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT email FROM employees WHERE activation_token = %s", [token])
            row = cursor.fetchone()
            if row:
                email = row[0]

                
                    # Retrieve the password from the JSON data
                password = request.data.get('password')

                    # Validate the password (you can add your own validation logic)

                    # Hash the password using Django's make_password function
                hashed_password = make_password(password)

                    # Update the password and activate the account in the database
                cursor.execute("UPDATE employees SET password = %s, isActive= True, activation_token = NULL WHERE email = %s", [hashed_password, email])
                connections['default'].commit()

                    # Return a JSON response indicating success
                return Response({'message': 'Password set successfully'})

            

            else:
                # Handle invalid or expired token
                return Response({"message:Invalid token"},status=400)       

class login(APIView):
    def post(self,request):
        email=request.data.get('email')
        password=request.data.get('password')
        
        # Query the database to retrieve the user's email and password
        with connections['default'].cursor() as cursor:
            cursor.execute("""
                           SELECT id,email,password,isActive FROM employees
                           WHERE email=%s
                           """,[email])
            row=cursor.fetchone()
            if row:
                user_id,user_email,user_password,isActive=row
                if isActive==False:
                    return Response({"message:Account is not activated"},status=400)
                else:    
                    # Check if the password is correct
                    if check_password(password,user_password):
                        #store user's session
                        # Generate a session key
                        session_key = get_random_string(length=32)

                    # Insert a new session record into the "sessions" table with session key and user ID recorded
                        with connections['default'].cursor() as cursor:
                            cursor.execute("INSERT INTO sessions (session_key, user_id) VALUES (%s, %s)", [session_key, user_id])
                            connections['default'].commit()
                            
                            response=Response({"message:Login successful"},status=200)
                            #store cookie in the browser
                            response.set_cookie('sessionid',session_key)
                        
                        return response
                    else:
                        return Response({"message:Invalid password"},status=400)
            else:
                return Response({"message:User not found"},status=400)
            
class logout(APIView):
    def delete(self,request):
        session_key=request.COOKIES.get('sessionid')
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute("DELETE FROM sessions WHERE session_key=%s",[session_key])
                connections['default'].commit()
            return Response({"message:Logged out successfully"},status=200)  
        except:
            return Response({"message:Please log in first"},status=400)  
        
class profile_view(APIView):
        
    def get(self,request):
        # Retrieve the session key from the request
        session_key = request.COOKIES.get('sessionid')
      
        # Query the "sessions" table using the session key to retrieve the user ID
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT user_id FROM sessions WHERE session_key = %s", [session_key])
            row = cursor.fetchone()

            if row:
                user_id = row[0]
                

                # Fetch user information from the "employees" table using the user ID
                with connections['default'].cursor() as cursor:
                    cursor.execute("SELECT * FROM employees WHERE id = %s", [user_id])
                    user_row = cursor.fetchone()
                    if user_row:
                        employee = {
                            'email': user_row[1],
                            'isManager': user_row[3],
                            'age': user_row[4],
                        } 
                        return Response(employee, status=200)

        # Handle invalid or expired session key
        return Response({"message": "Login first"}, status=400)
    
class profile_edit(APIView):    
    def put(self,request):
        session_key = request.COOKIES.get('sessionid')
      
        # Query the "sessions" table using the session key to retrieve the user ID
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT user_id FROM sessions WHERE session_key = %s", [session_key])
            row = cursor.fetchone()

            if row:
                id = row[0]
                # Update only those fields that are present in the request data
            
                with connections['default'].cursor() as cursor:
                    update_query = "UPDATE employees SET "
                    params = []
                    
                    if 'email' in request.data:
                        update_query += "email = %s, "
                        params.append(request.data['email'])
                    
                    if 'ismanager' in request.data:
                        update_query += "isManager = %s, "
                        params.append(request.data['ismanager'])
                    
                    if 'age' in request.data:
                        update_query += "age = %s, "
                        params.append(request.data['age'])
                    
                    # Remove the trailing comma and space from the query
                    update_query = update_query.rstrip(', ')
                    
                    if len(params) == 0:
                        return HttpResponse("No fields to update", status=400)
                    
                    update_query += " WHERE id = %s"
                    params.append(id)
                    cursor.execute(update_query, params)
                    rows_affected = cursor.rowcount

                    if rows_affected == 0:
                        return Response("Employee does not exist", status=404)
                    else:
                        connections['default'].commit()
                        return Response("Employee updated successfully")
            else:
                return Response({"message:Please log in first"},status=400)
        

class deactivate_account(APIView):
         
    def delete(self,request):
        session_id=request.COOKIES.get('sessionid')
        # Query the "sessions" table using the session key to retrieve the user ID
        with connections['default'].cursor() as cursor:
            cursor.execute("""
                           SELECT user_id FROM sessions WHERE session_key=%s
                           """,[session_id])
            row=cursor.fetchone()
            
            if row:
                id=row[0]
                # Update the isActive field to False in the database
                with connections['default'].cursor() as cursor:
                    cursor.execute("""
                                   UPDATE employees SET isActive=False WHERE id=%s
                                   """,[id])
                    connections['default'].commit()
                
                #delete the session record from cookies
                response=Response({"message:Account deactivated successfully"},status=200)
                response.delete_cookie('sessionid')
                
                return response
            else:
                return Response({"message:Please log in first"},status=400)
                
                    
            
    

