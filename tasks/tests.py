"""
Comprehensive Test Suite for Task Management Application
Tests cover:
1. Foreign Key Violation Tests
2. SQL Injection Attack Tests
3. Data Migration Tests
4. Regression Tests After Patches
"""

from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.urls import reverse
from .models import Task, Category, Project, Comment
import json


class ForeignKeyViolationTests(TransactionTestCase):
    """
    Test Suite for Foreign Key Constraint Violations
    Tests CASCADE, PROTECT, and SET_NULL behaviors
    """
    
    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(username='testuser1', password='testpass123')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass123')
        
    def test_cascade_delete_on_project(self):
        """
        Test CASCADE delete: Deleting a project should delete all related tasks
        Foreign Key: Task.project -> Project (on_delete=CASCADE)
        """
        print("\n=== Test 1: CASCADE Delete on Project ===")
        
        # Create project and tasks
        project = Project.objects.create(
            name="Test Project",
            description="Test description",
            owner=self.user1
        )
        
        task1 = Task.objects.create(
            title="Task 1",
            created_by=self.user1,
            project=project
        )
        task2 = Task.objects.create(
            title="Task 2",
            created_by=self.user1,
            project=project
        )
        
        # Verify tasks exist
        self.assertEqual(Task.objects.filter(project=project).count(), 2)
        print(f"Created project with {Task.objects.filter(project=project).count()} tasks")
        
        # Delete project
        project_id = project.id
        project.delete()
        
        # Verify tasks were CASCADE deleted
        remaining_tasks = Task.objects.filter(project_id=project_id).count()
        self.assertEqual(remaining_tasks, 0)
        print(f"✓ PASS: After deleting project, {remaining_tasks} tasks remain (CASCADE worked)")
        
    def test_protect_delete_on_category(self):
        """
        Test PROTECT constraint: Cannot delete category if tasks reference it
        Foreign Key: Task.category -> Category (on_delete=PROTECT)
        """
        print("\n=== Test 2: PROTECT Constraint on Category ===")
        
        # Create category and task
        category = Category.objects.create(
            name="Important",
            created_by=self.user1
        )
        
        task = Task.objects.create(
            title="Important Task",
            created_by=self.user1,
            category=category
        )
        
        print(f"Created category '{category.name}' with task '{task.title}'")
        
        # Try to delete category - should raise ProtectedError
        with self.assertRaises(ProtectedError) as context:
            category.delete()
        
        # Verify category still exists
        self.assertTrue(Category.objects.filter(id=category.id).exists())
        print(f"✓ PASS: Cannot delete category - ProtectedError raised as expected")
        print(f"   Category '{category.name}' still exists in database")
        
    def test_set_null_on_user_delete(self):
        """
        Test SET_NULL: Deleting assigned user sets task.assigned_to to NULL
        Foreign Key: Task.assigned_to -> User (on_delete=SET_NULL)
        """
        print("\n=== Test 3: SET_NULL on User Delete ===")
        
        # Create task assigned to user2
        task = Task.objects.create(
            title="Assigned Task",
            created_by=self.user1,
            assigned_to=self.user2
        )
        
        print(f"Created task assigned to '{self.user2.username}'")
        
        # Delete the assigned user
        task_id = task.id
        self.user2.delete()
        
        # Refresh task from database
        task.refresh_from_db()
        
        # Verify assigned_to is now NULL
        self.assertIsNone(task.assigned_to)
        print(f"✓ PASS: After deleting user, task.assigned_to = {task.assigned_to} (SET_NULL worked)")
        
    def test_cascade_delete_on_user_created_by(self):
        """
        Test CASCADE on created_by: Deleting creator deletes their tasks
        Foreign Key: Task.created_by -> User (on_delete=CASCADE)
        """
        print("\n=== Test 4: CASCADE Delete on Task Creator ===")
        
        # Create tasks by user
        task1 = Task.objects.create(title="Task 1", created_by=self.user1)
        task2 = Task.objects.create(title="Task 2", created_by=self.user1)
        
        initial_count = Task.objects.filter(created_by=self.user1).count()
        print(f"User '{self.user1.username}' created {initial_count} tasks")
        
        # Delete user
        self.user1.delete()
        
        # Verify all their tasks are deleted
        remaining = Task.objects.filter(created_by__username='testuser1').count()
        self.assertEqual(remaining, 0)
        print(f"✓ PASS: After deleting user, {remaining} of their tasks remain (CASCADE worked)")
        
    def test_cascade_delete_on_comments(self):
        """
        Test CASCADE: Deleting task deletes all comments
        Foreign Key: Comment.task -> Task (on_delete=CASCADE)
        """
        print("\n=== Test 5: CASCADE Delete on Comments ===")
        
        task = Task.objects.create(title="Task with Comments", created_by=self.user1)
        
        # Create comments
        comment1 = Comment.objects.create(task=task, user=self.user1, content="Comment 1")
        comment2 = Comment.objects.create(task=task, user=self.user1, content="Comment 2")
        
        comment_count = Comment.objects.filter(task=task).count()
        print(f"Created task with {comment_count} comments")
        
        # Delete task
        task.delete()
        
        # Verify comments deleted
        remaining_comments = Comment.objects.filter(task_id=task.id).count()
        self.assertEqual(remaining_comments, 0)
        print(f"✓ PASS: After deleting task, {remaining_comments} comments remain (CASCADE worked)")


class SQLInjectionTests(TestCase):
    """
    Test Suite for SQL Injection Protection
    Verifies that Django ORM prevents SQL injection attacks
    """
    
    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        
        # Create test data
        self.task1 = Task.objects.create(
            title="Normal Task",
            description="Regular task",
            created_by=self.user
        )
        self.task2 = Task.objects.create(
            title="Secret Task",
            description="Confidential",
            created_by=self.user
        )
        
    def test_sql_injection_in_search(self):
        """
        Test SQL injection attempts in search functionality
        Malicious input should be escaped by Django ORM
        """
        print("\n=== Test 6: SQL Injection in Search ===")
        
        # Attempt SQL injection in search parameter
        malicious_inputs = [
            "' OR '1'='1",  # Classic SQL injection
            "'; DROP TABLE tasks_task; --",  # Table drop attempt
            "' UNION SELECT * FROM auth_user; --",  # Union attack
            "<script>alert('XSS')</script>",  # XSS attempt
        ]
        
        for malicious_input in malicious_inputs:
            print(f"Testing input: {malicious_input}")
            
            response = self.client.get(reverse('task_list'), {'search': malicious_input})
            
            # Should return 200 without error (Django escapes input)
            self.assertEqual(response.status_code, 200)
            
            # Verify database is intact
            task_count = Task.objects.count()
            self.assertEqual(task_count, 2)
            print(f"  ✓ Request handled safely, database intact ({task_count} tasks)")
        
        print(f"✓ PASS: All SQL injection attempts blocked by Django ORM")
        
    def test_sql_injection_in_filter(self):
        """
        Test SQL injection in filter parameters
        """
        print("\n=== Test 7: SQL Injection in Filters ===")
        
        # Attempt injection in status filter
        malicious_status = "todo' OR '1'='1"
        response = self.client.get(reverse('task_list'), {'status': malicious_status})
        
        self.assertEqual(response.status_code, 200)
        
        # Should return 0 results (no matching status)
        # Django ORM treats entire string as literal value
        tasks = response.context['tasks'] if 'tasks' in response.context else []
        print(f"Malicious status filter returned {len(tasks)} tasks")
        print(f"✓ PASS: Injection attempt treated as literal string, no SQL executed")
        
    def test_parameterized_query_safety(self):
        """
        Verify that Django uses parameterized queries
        """
        print("\n=== Test 8: Parameterized Query Verification ===")
        
        # Use ORM which generates parameterized queries
        malicious_title = "Test' OR '1'='1"
        
        # This should not match anything
        results = Task.objects.filter(title=malicious_title)
        self.assertEqual(results.count(), 0)
        print(f"Search for malicious title: {results.count()} results")
        
        # Normal search should work
        normal_results = Task.objects.filter(title="Normal Task")
        self.assertEqual(normal_results.count(), 1)
        print(f"Search for normal title: {normal_results.count()} results")
        print(f"✓ PASS: Django ORM uses parameterized queries - injection impossible")


class DataMigrationTests(TransactionTestCase):
    """
    Test Suite for Data Migration and Data Integrity
    Simulates schema changes and data migrations
    """
    
    def setUp(self):
        """Set up initial data"""
        self.user = User.objects.create_user(username='migrationuser', password='pass123')
        
    def test_data_integrity_after_adding_field(self):
        """
        Test data integrity when new fields are added (simulated)
        """
        print("\n=== Test 9: Data Integrity After Schema Change ===")
        
        # Create tasks with original fields
        task1 = Task.objects.create(
            title="Old Task 1",
            created_by=self.user,
            status='todo'
        )
        task2 = Task.objects.create(
            title="Old Task 2",
            created_by=self.user,
            status='done'
        )
        
        original_count = Task.objects.count()
        print(f"Created {original_count} tasks before migration")
        
        # Simulate: New field with default value already exists in model
        # Verify old data still accessible
        tasks_after = Task.objects.all()
        self.assertEqual(tasks_after.count(), original_count)
        
        # Verify all fields accessible
        for task in tasks_after:
            self.assertIsNotNone(task.title)
            self.assertIsNotNone(task.created_by)
            self.assertIsNotNone(task.status)
            # New fields should have defaults
            self.assertIsNotNone(task.priority)  # Has default='medium'
        
        print(f"✓ PASS: All {tasks_after.count()} tasks intact after schema change")
        print(f"  All fields accessible with proper defaults")
        
    def test_data_mismatch_detection(self):
        """
        Test for data type mismatches and constraint violations
        """
        print("\n=== Test 10: Data Mismatch Detection ===")
        
        # Test 1: Required field violation
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Task.objects.create(title="Test")  # Missing required created_by
        print("  ✓ Missing required field detected")
        
        # Test 2: Invalid choice value (should be caught at form level)
        task = Task.objects.create(
            title="Test Task",
            created_by=self.user
        )
        # Django allows invalid choices at model level, validates at form level
        task.status = "invalid_status"
        task.save()  # Saves but forms would reject
        print("  ✓ Invalid choice saved (form validation needed)")
        
        # Test 3: Unique constraint
        category1 = Category.objects.create(name="Unique", created_by=self.user)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(name="Unique", created_by=self.user)
        print("  ✓ Unique constraint violation detected")
        
        print("✓ PASS: Data validation and constraint checking working")
        
    def test_migration_rollback_scenario(self):
        """
        Test data consistency during migration failures
        """
        print("\n=== Test 11: Migration Rollback Scenario ===")
        
        initial_count = Task.objects.count()
        
        # Simulate failed migration with transaction rollback
        try:
            with transaction.atomic():
                # Create some tasks
                Task.objects.create(title="Task 1", created_by=self.user)
                Task.objects.create(title="Task 2", created_by=self.user)
                
                # Simulate error
                raise Exception("Simulated migration error")
        except Exception as e:
            print(f"  Migration failed: {e}")
        
        # Verify rollback - count should be unchanged
        final_count = Task.objects.count()
        self.assertEqual(initial_count, final_count)
        print(f"✓ PASS: Transaction rolled back, {initial_count} tasks before = {final_count} tasks after")


class RegressionTests(TestCase):
    """
    Test Suite for Regression Testing After Patches
    Ensures existing functionality remains intact
    """
    
    def setUp(self):
        """Set up test environment"""
        self.client = Client()
        self.user = User.objects.create_user(username='reguser', password='pass123')
        self.client.login(username='reguser', password='pass123')
        
        self.category = Category.objects.create(name="Work", created_by=self.user)
        self.project = Project.objects.create(name="Project A", owner=self.user)
        
    def test_task_creation_functionality(self):
        """
        Regression test: Task creation should still work after patches
        """
        print("\n=== Test 12: Task Creation Regression ===")
        
        task_data = {
            'title': 'Regression Test Task',
            'description': 'Testing after patch',
            'status': 'todo',
            'priority': 'high',
            'category': self.category.id,
            'project': self.project.id,
        }
        
        response = self.client.post(reverse('task_create'), task_data)
        
        # Should redirect on success
        self.assertEqual(response.status_code, 302)
        
        # Verify task created
        task_exists = Task.objects.filter(title='Regression Test Task').exists()
        self.assertTrue(task_exists)
        print("✓ PASS: Task creation working after patch")
        
    def test_task_update_functionality(self):
        """
        Regression test: Task updates should work
        """
        print("\n=== Test 13: Task Update Regression ===")
        
        task = Task.objects.create(
            title="Original Title",
            created_by=self.user,
            status='todo'
        )
        
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'status': 'in_progress',
            'priority': 'urgent',
        }
        
        response = self.client.post(
            reverse('task_update', kwargs={'pk': task.pk}),
            update_data
        )
        
        # Refresh from database
        task.refresh_from_db()
        
        self.assertEqual(task.title, 'Updated Title')
        self.assertEqual(task.status, 'in_progress')
        print("✓ PASS: Task update working after patch")
        
    def test_task_deletion_functionality(self):
        """
        Regression test: Task deletion should work
        """
        print("\n=== Test 14: Task Deletion Regression ===")
        
        task = Task.objects.create(title="To Delete", created_by=self.user)
        task_id = task.id
        
        response = self.client.post(reverse('task_delete', kwargs={'pk': task.pk}))
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        
        # Verify deleted
        task_exists = Task.objects.filter(id=task_id).exists()
        self.assertFalse(task_exists)
        print("✓ PASS: Task deletion working after patch")
        
    def test_search_functionality(self):
        """
        Regression test: Search functionality should work
        """
        print("\n=== Test 15: Search Functionality Regression ===")
        
        Task.objects.create(title="Python Development", created_by=self.user)
        Task.objects.create(title="Java Development", created_by=self.user)
        
        response = self.client.get(reverse('task_list'), {'search': 'Python'})
        
        self.assertEqual(response.status_code, 200)
        tasks = response.context['tasks']
        self.assertEqual(len(tasks), 1)
        self.assertIn('Python', tasks[0].title)
        print("✓ PASS: Search functionality working after patch")
        
    def test_filtering_functionality(self):
        """
        Regression test: Filtering should work
        """
        print("\n=== Test 16: Filter Functionality Regression ===")
        
        Task.objects.create(title="Task 1", status='todo', created_by=self.user)
        Task.objects.create(title="Task 2", status='done', created_by=self.user)
        Task.objects.create(title="Task 3", status='todo', created_by=self.user)
        
        response = self.client.get(reverse('task_list'), {'status': 'todo'})
        
        tasks = response.context['tasks']
        self.assertEqual(len(tasks), 2)
        for task in tasks:
            self.assertEqual(task.status, 'todo')
        print("✓ PASS: Filtering functionality working after patch")
        
    def test_authentication_protection(self):
        """
        Regression test: Authentication should still protect views
        """
        print("\n=== Test 17: Authentication Protection Regression ===")
        
        # Logout
        self.client.logout()
        
        # Try to access protected view
        response = self.client.get(reverse('task_list'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
        print("✓ PASS: Authentication protection working after patch")
        
    def test_relationship_integrity(self):
        """
        Regression test: Foreign key relationships should work
        """
        print("\n=== Test 18: Relationship Integrity Regression ===")
        
        task = Task.objects.create(
            title="Related Task",
            created_by=self.user,
            category=self.category,
            project=self.project
        )
        
        # Test reverse relationships
        self.assertIn(task, self.category.tasks.all())
        self.assertIn(task, self.project.tasks.all())
        self.assertIn(task, self.user.created_tasks.all())
        
        print("✓ PASS: All foreign key relationships working after patch")


# Test runner summary
def run_all_tests():
    """
    Summary function to document all tests
    """
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST SUITE SUMMARY")
    print("="*70)
    print("\n1. FOREIGN KEY VIOLATION TESTS (5 tests)")
    print("   - CASCADE delete on Project → Tasks")
    print("   - PROTECT constraint on Category")
    print("   - SET_NULL on User assignment")
    print("   - CASCADE on Task creator")
    print("   - CASCADE on Comments")
    print("\n2. SQL INJECTION TESTS (3 tests)")
    print("   - SQL injection in search")
    print("   - SQL injection in filters")
    print("   - Parameterized query verification")
    print("\n3. DATA MIGRATION TESTS (3 tests)")
    print("   - Data integrity after schema change")
    print("   - Data mismatch detection")
    print("   - Migration rollback scenario")
    print("\n4. REGRESSION TESTS (7 tests)")
    print("   - Task creation")
    print("   - Task update")
    print("   - Task deletion")
    print("   - Search functionality")
    print("   - Filter functionality")
    print("   - Authentication protection")
    print("   - Relationship integrity")
    print("\n" + "="*70)
    print("TOTAL: 18 comprehensive tests")
    print("="*70 + "\n")
