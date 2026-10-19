from datetime import datetime



from models import Classroom, Event, User





def test_user_has_student_role_by_default():
  
    user = User(name="Ana", email="ana@example.com")
  


    assert user.role == "student"
  
    assert user.id is None
  




def test_classroom_stores_basic_data():
  
    classroom = Classroom(name="INFO4V", description="Turma de informática")
  


    assert classroom.name == "INFO4V"
  
    assert classroom.description == "Turma de informática"
  




def test_event_links_to_a_classroom():
  
    start = datetime(2026, 10, 20, 19, 0)
  
    end = datetime(2026, 10, 20, 21, 0)
  
    event = Event(
      
        title="Aula de projeto",
      
        start_at=start,
      
        end_at=end,
      
        classroom_id=1,
      
    )
  


    assert event.classroom_id == 1
  
    assert event.start_at < event.end_at
  



















