class Blackboard:
   def __init__(self, max_entries=12):
      self.max_entries = max_entries 
      self.entries = [] 
      
   def add(self, round, agent, content):
      self.entries.append((round, agent, content))
      if len(self.entries) > self.max_entries: 
         self.entries.pop(0) #pop the oldest entry 
         
   def transcript(self, exclude_agent=None):
      relevant_entries = [entry for entry in self.entries if entry[1] != exclude_agent]
      transfer_variable = "\n".join(f"{e[1]} (Round {e[0]}): {e[2]}" for e in relevant_entries)
      return transfer_variable
         
   def full_transcript(self): 
      return "\n".join(f"{e[1]} (Round {e[0]}): {e[2]}" for e in self.entries)
   
   
