# >>> exec(open("db_additional.py").read())

from MonkeyBook.models import db
from MonkeyBook.models import Monkey
import random

names = ['Amanda Blake',         
         'Jamie Ortiz',          
         'Kerry Snyder',         
         'Marsha Morton',        
         'Sheryl Phelps',        
         'Johnathan Pierce',     
         'Guy Moreno',           
         'Lynn Black',           
         'Lamar Gonzales',       
         'Kim Burns',            
         'Angie Gilbert',        
         'Micheal Hayes',        
         'Pamela Bailey',        
         'Mark Buchanan',        
         'Shannon Francis',      
         'Shirley Morales',      
         'Flora Briggs',         
         'Natalie Lambert',      
         'Frank Oliver',         
         'Kristopher Rose',      
         'Roman Swanson',        
         'Anita Graham',         
         'Esther Figueroa',      
         'Evelyn Jordan',        
         'Eduardo Ryan',         
         'Anna Osborne',         
         'Bradford Doyle',       
         'Bob Stanley',          
         'Jerald Huff',          
         'Elias Austin',         
         'Darrin Maxwell',       
         'Lindsey Owen',         
         'Mindy Mcdaniel',       
         'Lorraine Jackson',     
         'Jamie Ruiz',           
         'Lance Maldonado',      
         'Janet Burgess',        
         'Kerry Mcguire',        
         'Jon Johnston',         
         'Barbara Gomez',        
         'Eleanor Hopkins',      
         'Ray Marsh',            
         'Blake Parker',         
         'Felix Mccormick',      
         'Moses Payne',          
         'Jesse Ingram',         
         'Joann Williams',       
         'Nancy Horton',         
         'Joseph Russell',       
         'Kathryn Gibson',       
         'Jacob Phillips',       
         'Oscar Singleton',      
         'Scott Barnett',        
         'Randall Moss',         
         'Bessie Nash',          
         'Spencer Cortez',       
         'Chad Powell',          
         'Marguerite Mills',     
         'Elaine Bishop',        
         'Kay Mckinney',         
         'Leroy Hughes',         
         'Catherine Hudson',     
         'Cynthia Summers',      
         'Kevin Reid',           
         'Gwen Wheeler',         
         'Maggie Fernandez',     
         'Sophia Neal',          
         'Mary Herrera',         
         'Debbie Logan',         
         'Guadalupe Mckenzie',   
         'Emmett Lewis',         
         'Lee Moran',            
         'Mattie Wilkerson',     
         'Phyllis Rogers',       
         'Kristi Hodges',        
         'Boyd Cook',            
         'Preston Schneider',    
         'Andres Thomas',        
         'Rhonda Lucas',         
         'Jeff Stokes',          
         'Hope Rios',            
         'Bradley Carson',       
         'Josefina Hale',        
         'Charlotte Goodwin',    
         'Maria Graves',         
         'Luz Boyd',             
         'Gwendolyn Watts',      
         'Jessie Barrett',       
         'Martha Park',          
         'Louis Rodgers',        
         'John Erickson',        
         'Jasmine Bridges',      
         'Pat Watkins',          
         'Judith Delgado',       
         'Rachel West',          
         'Abraham Frank',        
         'Myron Cohen',          
         'Felipe Tucker',        
         'Inez Perry',           
         'Darlene Cruz']

monkeys = list()

for name in names:
    name_split = name.split()
    monkey = Monkey(name_split[0],
                    name_split[1],
                    '123',
                    name_split[0].lower() + '.' + name_split[1].lower() + '@email.com',
                    str(random.randint(1950, 2014)) + '-' + str(random.randint(1, 12)) + '-' + str(random.randint(1, 28)))
    monkeys.append(monkey)

for monkey in monkeys:
    db.session.add(monkey)

    # Up to 20 friends
    for i in range(random.randint(0, 20)):
        potential_friend = monkeys[random.randint(0, len(monkeys) - 1)]
        if potential_friend is not monkey and potential_friend not in monkey.friends:
            monkey.friends.append(potential_friend)

    # 2:1 chance of having a best friend
    if monkey.friends and random.randint(0, 2):
        monkey.best_friend = monkey.friends[random.randint(0, len(monkey.friends) - 1)]

db.session.commit()
