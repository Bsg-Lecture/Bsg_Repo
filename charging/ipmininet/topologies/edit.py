import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import yaml
from PIL import Image, ImageTk

try:
    with open(f'charging/ipmininet/topologies/customTopo_config.yaml', 'r') as file:
            config = yaml.safe_load(file)
except:
    data = '''
    clients:
        client1:
            name: 'CLI1'
            version: 'v2.0.1'
            profile: 3
    servers:
        server1:
            name: 'server1'
            multiple: 2
            url: 'ocpp-simulator.com'
            dns: 'DNS1'
    routers:
        router1:
            name: 'R1'
    links:
        - ['server1', 'R1']
        - ['CLI1', 'R1']
    '''

    config = yaml.safe_load(data)

def find_element_by_name(name):
    if 'clients' in config.keys():
        if config['clients'] != None:
            for element_key, element_data in config['clients'].items():
                if element_data['name'] == name:
                    return element_key
    if 'servers' in config.keys():
        if config['servers'] != None:
            for element_key, element_data in config['servers'].items():
                if element_data['name'] == name:
                    return element_key
    if 'routers' in config.keys():
        if config['routers'] != None:
            for element_key, element_data in config['routers'].items():
                if element_data['name'] == name:
                    return element_key
    if 'switches' in config.keys():
        if config['switches'] != None:
            for element_key, element_data in config['switches'].items():
                if element_data['name'] == name:
                    return element_key
    if 'hosts' in config.keys():
        if config['hosts'] != None:
            for element_key, element_data in config['hosts'].items():
                if element_data['name'] == name:
                    return element_key
    if 'dns' in config.keys():
        if config['dns'] != None:
            for element_key, element_data in config['dns'].items():
                if element_data['name'] == name:
                    return element_key
    return None

class DragDropCanvas(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.client_img = self.load_and_resize_image("./charging/ipmininet/pictures/cp.png", 75, 75)  
        self.server_img = self.load_and_resize_image("./charging/ipmininet/pictures/server.png", 75, 75)   
        self.router_img = self.load_and_resize_image("./charging/ipmininet/pictures/router.png", 75, 75)  
        self.switch_img = self.load_and_resize_image("./charging/ipmininet/pictures/switch.png", 75, 75)   
        self.dns_image = self.load_and_resize_image("./charging/ipmininet/pictures/dns.png", 75, 75)
        self.host_image = self.load_and_resize_image("./charging/ipmininet/pictures/host.png", 75, 75)     
                                                    
        self.parent = parent
        self.config(width=1000, height=700, bg="white")
        self.pack(fill="both", expand=True)

        self.elements = {}
        self.connections = []
        self.selected_element = None
        self.connect_mode = False
        self.start_element = None  

        # Bind events for dragging and selecting
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Button-4>", lambda event: self.zoom(scale_factor=1.1))
        self.bind("<Button-5>", lambda event: self.zoom(scale_factor=0.9))
        self.pan_start = None 
        self.dragging_element = False 
        
        
        # Bind right-click for context menu
        self.bind("<Button-3>", self.show_context_menu)

        # Create a context menu for element modifications
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Delete Element", command=self.delete_element)
        self.context_menu.add_command(label="Delete Link", command=self.delete_link)
        self.context_menu.add_command(label="Modify", command=self.modify_element)

    def load_and_resize_image(self, path, width, height):
            """Load an image and resize it to the given width and height."""
            img = Image.open(path)
            img = img.resize((width, height),  Image.Resampling.LANCZOS)  # Resize with anti-aliasing
            return ImageTk.PhotoImage(img)
    
    def add_element(self, name, element_type, x, y):
        """Add an element (client, server, or router) with an icon and text"""
        if element_type == "server":
            icon = self.create_image(x, y, image=self.server_img, anchor=tk.CENTER, tags=name)
        elif element_type == "client":
            icon = self.create_image(x, y, image=self.client_img, anchor=tk.CENTER, tags=name)
        elif element_type == "router":
            icon = self.create_image(x, y, image=self.router_img, anchor=tk.CENTER, tags=name)
        elif element_type == "switch":
            icon = self.create_image(x, y, image=self.switch_img, anchor=tk.CENTER, tags=name)
        elif element_type == "dns":
            icon = self.create_image(x, y, image=self.dns_image, anchor=tk.CENTER, tags=name)
        elif element_type == "host":
            icon = self.create_image(x, y, image=self.host_image, anchor=tk.CENTER, tags=name)

        label = self.create_text(x, y+50, text=name, tags=name)
        self.elements[name] = (icon, label, [])


    def on_click(self, event):
        """Select an element to drag or create connections"""

        try:
            self.context_menu.unpost()
        except:
            pass

        canvas_x = self.canvasx(event.x) 
        canvas_y = self.canvasy(event.y) 
        overlapping_items = self.find_overlapping(canvas_x, canvas_y, canvas_x, canvas_y)

        if len(overlapping_items) > 0:
            self.dragging_element = True
            for element in self.elements:
                if self.elements[element][0]==overlapping_items[0]:
                    self.selected_element = element  # Store the name of the selected element
                    icon, label, connections = self.elements[self.selected_element]
                    dx = self.coords(icon)[0]
                    dy = self.coords(icon)[1]
            # If in connect mode, store the starting element
            if self.connect_mode:
                if not self.start_element:
                    self.start_element = self.selected_element
                else:
                    # Draw a connection and reset start_element
                    self.add_connection(self.start_element, self.selected_element)
                    self.start_element = None
        else:
            self.dragging_element = False
            self.pan_start = (event.x, event.y)
            self.scan_mark(event.x, event.y)

    def on_drag(self, event):
        """Drag the selected element and move its connections"""
        if self.dragging_element:
            if self.selected_element:
                icon, label, connections = self.elements[self.selected_element]
                dx = self.canvasx(event.x)- self.coords(icon)[0]
                dy = self.canvasy(event.y)- self.coords(icon)[1]
                self.move(icon, dx, dy)  # Move the icon
                self.move(label, dx, dy)  # Move the label with the icon
                # Move connections as well
                for line, other_element in connections:
                    self.update_connection_position(line, self.selected_element, other_element)
        elif self.pan_start:
            self.scan_dragto(event.x, event.y, gain=2)

    def update_scroll_region(self):
        """Ensure the scroll region of the canvas is updated after panning."""
        self.update_idletasks()  # Ensures that the canvas gets updated

        # Get the new canvas view region and adjust scroll region accordingly
        x0, y0, x1, y1 = self.bbox("all")  # Get bounding box of all elements
        self.configure(scrollregion=(x0, y0, x1, y1))  # Update the scroll region

    def on_release(self, event):
        """Release the selected element after dragging"""
        if self.dragging_element:
            self.selected_element = None
        else:
            self.pan_start = None


    def add_connection(self, element1, element2, start = True):
        """Draw a connection (line) between two elements and update YAML"""
        if element1 == element2:
            messagebox.showerror("Error", "Cannot connect an element to itself.")
            return

        # Avoid duplicate connections
        if start:
            for line, connected_element in self.elements[element1][2]:
                if connected_element == element2:
                    messagebox.showerror("Error", "This connection already exists.")
                    return

        if element1 in self.elements and element2 in self.elements:
            line = self.create_line_between_elements(element1, element2)
            self.elements[element1][2].append((line, element2))
            self.elements[element2][2].append((line, element1))
            if start:
                # Fetch the 'name' field from the config (clients, servers, or routers)
                name1 = (config['clients'].get(find_element_by_name(element1)) or 
                        config['servers'].get(find_element_by_name(element1)) or 
                        config['routers'].get(find_element_by_name(element1)) or
                        config['switches'].get(find_element_by_name(element1)) or
                        config['dns'].get(find_element_by_name(element1)) or
                        config['hosts'].get(find_element_by_name(element1))).get('name')
                name2 = (config['clients'].get(find_element_by_name(element2)) or 
                        config['servers'].get(find_element_by_name(element2)) or 
                        config['routers'].get(find_element_by_name(element2)) or
                        config['switches'].get(find_element_by_name(element2)) or
                        config['dns'].get(find_element_by_name(element2)) or
                        config['hosts'].get(find_element_by_name(element2))).get('name')

                # Update YAML config with the names of the elements
                if 'links' not in config:
                    config['links'] = []

                config['links'].append([name1, name2])


    def create_line_between_elements(self, element1, element2):
        """Create a line between two elements from their centers"""
        x1, y1, x2, y2 = self.bbox(self.elements[element1][0])  # Get bounding box of element1
        x3, y3, x4, y4 = self.bbox(self.elements[element2][0])  # Get bounding box of element2
        line = self.create_line((x1+x2)/2, (y1+y2)/2, (x3+x4)/2, (y3+y4)/2, fill="black", width=3)
        
        # Move the line behind other elements
        self.tag_lower(line)
        
        return line

    def update_connection_position(self, line, element1, element2):
        """Update the position of a connection (line) when an element moves"""
        x1, y1, x2, y2 = self.bbox(self.elements[element1][0])  # Get bounding box of element1
        x3, y3, x4, y4 = self.bbox(self.elements[element2][0])  # Get bounding box of element2
        self.coords(line, (x1+x2)//2, (y1+y2)//2, (x3+x4)//2, (y3+y4)//2)

    def delete_element(self):
        """Delete the selected element and all its connections"""
        if self.selected_element:
            icon, label, connections = self.elements[self.selected_element]
            self.delete(icon)
            self.delete(label)

            # Delete all connections associated with this element
            for line, other_element in connections:
                self.delete(line)
                # Remove the connection from the other element
                other_icon, other_label, other_connections = self.elements[other_element]
                self.elements[other_element] = (other_icon, other_label, [conn for conn in other_connections if conn[1] != self.selected_element])

            # Remove the element from the dictionary
            del self.elements[self.selected_element]

            # Remove element from the YAML configuration
            if config['clients'] != None and self.selected_element in config['clients']:
                del config['clients'][self.selected_element]
            elif config['servers'] != None and self.selected_element in config['servers']:
                del config['servers'][self.selected_element]
            elif config['routers'] != None and self.selected_element in config['routers']:
                del config['routers'][self.selected_element]
            elif config['switches'] != None and self.selected_element in config['switches']:
                del config['switches'][self.selected_element]
            elif config['hosts'] != None and self.selected_element in config['hosts']:
                del config['hosts'][self.selected_element]
            elif config['dns'] != None and self.selected_element in config['dns']:
                del config['dns'][self.selected_element]

            # Remove all links associated with the element from the YAML configuration
            if 'links' in config.keys():
                for orig, dest in config['links']:
                    if self.selected_element == orig or self.selected_element == dest:
                        config['links'].remove([orig, dest])

            self.selected_element = None

    def delete_link(self):
        """Delete a link between two elements"""
        if self.selected_element:
            connections = self.elements[self.selected_element][2]
            if not connections:
                messagebox.showerror("Error", "No links to delete.")
                return

            # Create a list of connected elements
            other_elements = [conn[1] for conn in connections]

            # Create a simple dialog to choose from connected elements
            def select_element():
                # Selection dialog
                dialog = tk.Toplevel(self)
                dialog.title("Select Element to Disconnect")
                label = tk.Label(dialog, text="Choose an element to disconnect:")
                label.pack(padx=20, pady=10)

                # Create a combobox (dropdown list)
                combobox = ttk.Combobox(dialog, values=other_elements, state="readonly")
                combobox.pack(padx=20, pady=10)

                # OK button
                def on_ok():
                    choice = combobox.get()
                    if choice:
                        self.delete_chosen_link(choice)
                    dialog.destroy()

                ok_button = tk.Button(dialog, text="OK", command=on_ok)
                ok_button.pack(padx=20, pady=10)

            select_element()

    def delete_chosen_link(self, choice):
        """Helper method to delete the selected link"""
        connections = self.elements[self.selected_element][2]
        for line, other_element in connections:
            if other_element == choice:
                self.delete(line)
                # Remove connection from both elements
                icon, label, _ = self.elements[self.selected_element]
                self.elements[self.selected_element] = (icon, label, [conn for conn in connections if conn[1] != other_element])

                icon2, label2, other_connections = self.elements[other_element]
                self.elements[other_element] = (icon2, label2, [conn for conn in other_connections if conn[1] != self.selected_element])

                # Remove the link from YAML
                for orig, dest in config['links']:
                    if (choice == orig and self.selected_element == dest) or (self.selected_element == orig and choice == dest):
                        config['links'].remove([orig, dest])
                break

    def modify_element(self):
        """Modify the properties of the selected element"""
        if self.selected_element:
            if config['clients'] != None and find_element_by_name(self.selected_element) in config['clients']:
                element_type = "client"
            elif config['servers'] != None and find_element_by_name(self.selected_element) in config['servers']:
                element_type = "server"
            elif config['routers'] != None and find_element_by_name(self.selected_element) in config['routers']:
                element_type = "router"
            elif config['switches'] != None and find_element_by_name(self.selected_element) in config['switches']:
                element_type = "switch"
            elif config['hosts'] != None and find_element_by_name(self.selected_element) in config['hosts']:
                element_type = "host"
            elif config['dns'] != None and find_element_by_name(self.selected_element) in config['dns']:
                element_type = "dns"
            else:
                return
            if element_type in ('client', 'server', 'router', 'host'):
                element_data = config[element_type + 's'][find_element_by_name(self.selected_element)]
            elif element_type == 'switch':
                element_data = config[element_type + 'es'][find_element_by_name(self.selected_element)]
            elif element_type == 'dns':
                element_data = config[element_type][find_element_by_name(self.selected_element)]

             # Create a new window for modifying the element
            dialog = tk.Toplevel()
            dialog.title(f"Modify {element_type.capitalize()}")

            # Create a container frame for scrollable content
            container = tk.Frame(dialog)
            container.grid(row=0, column=0, sticky="nsew")
            dialog.grid_rowconfigure(0, weight=1)
            dialog.grid_columnconfigure(0, weight=1)

            # Create a Canvas for adding scroll functionality
            canvas = tk.Canvas(container)
            canvas.grid(row=0, column=0, sticky="nsew")

            # Add a Scrollbar to the Canvas
            scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
            scrollbar.grid(row=0, column=1, sticky="ns")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Create a frame inside the Canvas
            scrollable_frame = tk.Frame(canvas)
            
            # Add the scrollable frame to the Canvas
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

            # Ensure the scrollable frame resizes with the canvas
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            
            # Configure grid expansion for the canvas to expand with window resizing
            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)

            # Name input
            tk.Label(scrollable_frame, text="Name").grid(row=0, column=0, padx=10, pady=5)
            name_entry = tk.Entry(scrollable_frame)
            name_entry.insert(0, element_data['name'])
            name_entry.grid(row=0, column=1, padx=10, pady=5)

            # Version input (only for client)
            if element_type == "client":
                tk.Label(scrollable_frame, text="Version").grid(row=1, column=0, padx=10, pady=5)
                version_combobox = ttk.Combobox(scrollable_frame, values=['v1.6', 'v2.0', 'v2.0.1'])
                version_combobox.set(element_data.get('version', 'v2.0.1'))  
                version_combobox.grid(row=1, column=1, padx=10, pady=5)

                # Profile input (only for client)
                tk.Label(scrollable_frame, text="Security Profile").grid(row=2, column=0, padx=10, pady=5)
                sprofile_entry = tk.Entry(scrollable_frame)
                sprofile_entry.insert(0, element_data.get('SecProfile'))
                sprofile_entry.grid(row=2, column=1, padx=10, pady=5)

            # Multiple input (only for server)
            elif element_type == "server":
                tk.Label(scrollable_frame, text="Multiple").grid(row=1, column=0, padx=10, pady=5)
                multiple_entry = tk.Entry(scrollable_frame)
                multiple_entry.insert(0, element_data.get('multiple', ''))
                multiple_entry.grid(row=1, column=1, padx=10, pady=5)

            if element_type in ('client', 'server'):
                # Checkbox for URL and DNS
                include_url_dns_var = tk.IntVar()
                include_url_dns_checkbox = tk.Checkbutton(scrollable_frame, text="Connect to DNS", variable=include_url_dns_var)
                include_url_dns_checkbox.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

                # URL input (conditionally displayed)
                url_label = tk.Label(scrollable_frame, text="URL")
                url_entry = tk.Entry(scrollable_frame)
                url_entry.insert(0, element_data.get('url', ''))

                # DNS input (conditionally displayed)
                dns_label = tk.Label(scrollable_frame, text="DNS")
                dns_entry = tk.Entry(scrollable_frame)
                dns_entry.insert(0, element_data.get('dns', ''))

                # Toggle URL and DNS visibility based on checkbox
                def toggle_url_dns():
                    if include_url_dns_var.get():
                        url_label.grid(row=4, column=0, padx=10, pady=5)
                        url_entry.grid(row=4, column=1, padx=10, pady=5)
                        dns_label.grid(row=5, column=0, padx=10, pady=5)
                        dns_entry.grid(row=5, column=1, padx=10, pady=5)
                    else:
                        url_label.grid_forget()
                        url_entry.grid_forget()
                        dns_label.grid_forget()
                        dns_entry.grid_forget()

                include_url_dns_var.trace_add('write', lambda *args: toggle_url_dns())
                if 'url' in element_data and 'dns' in element_data:
                    include_url_dns_var.set(1)
                    toggle_url_dns()
            
            if element_type == 'client':
                profiles = element_data.get('profiles', {})

                # Function to refresh the displayed profiles
                def refresh_profiles():
                    # Remove all existing profile entries
                    for widget in scrollable_frame.grid_slaves():
                        if int(widget.grid_info()["row"]) > 6 and int(widget.grid_info()["row"]) != 999:  # Remove profile-specific rows only
                            widget.grid_forget()

                    # Display profiles only if version is 'v2.0.1' or 'v2.0'
                    if version_combobox.get() in ('v2.0.1', 'v2.0'):
                        tk.Label(scrollable_frame, text="Network Configuration Priority").grid(row=7, column=0, padx=10, pady=5)
                        priority_entry = tk.Entry(scrollable_frame)
                        priority_entry.insert(0, ','.join(map(str, element_data.get('priority', []))))
                        priority_entry.grid(row=7, column=1, padx=10, pady=5)

                        tk.Label(scrollable_frame, text="Network Profile Connection Attempts").grid(row=8, column=0, padx=10, pady=5)
                        attempts_entry = tk.Entry(scrollable_frame)
                        attempts_entry.insert(0, element_data.get('attempts', []))
                        attempts_entry.grid(row=8, column=1, padx=10, pady=5)

                        tk.Label(scrollable_frame, text="Cert Signing Wait Minimum").grid(row=9, column=0, padx=10, pady=5)
                        wait_entry = tk.Entry(scrollable_frame)
                        wait_entry.insert(0, element_data.get('wait', []))
                        wait_entry.grid(row=9, column=1, padx=10, pady=5)

                        for i, profile in profiles.items():
                            profile_label = tk.Label(scrollable_frame, text=f"Profile {i}")
                            profile_label.grid(row=10+ int(i) * 5, column=0, padx=10, pady=5)

                            sp_label = tk.Label(scrollable_frame, text="SP")
                            sp_label.grid(row=11 + int(i) * 5, column=0, padx=10, pady=5)
                            sp_entry = tk.Entry(scrollable_frame)
                            sp_entry.insert(0, profile.get('SP', ''))
                            sp_entry.grid(row=11 + int(i) * 5, column=1, padx=10, pady=5)

                            ocpp_label = tk.Label(scrollable_frame, text="OCPP Version")
                            ocpp_label.grid(row=12 + int(i) * 5, column=0, padx=10, pady=5)
                            ocpp_combobox = ttk.Combobox(scrollable_frame, values=['OCPP16', 'OCPP20', 'OCPP201'])
                            if element_data.get('profiles') != None:
                                ocpp_combobox.set(element_data.get('profiles').get(i).get('ocpp_version', 'OCPP201'))  
                            else:
                                ocpp_combobox.set('OCPP201')  
                            ocpp_combobox.grid(row=12 + int(i) * 5, column=1, padx=10, pady=5)

                            # Button to remove profile
                            remove_button = tk.Button(scrollable_frame, text="Remove", command=lambda idx=i: remove_profile(idx))
                            remove_button.grid(row=11 + int(i) * 5, column=2, padx=10, pady=5)

                        # Add Profile Button
                        add_button = tk.Button(scrollable_frame, text="Add Profile", command=add_profile)
                        add_button.grid(row=10, column=0, padx=10, pady=5)

                # Function to remove a profile
                def remove_profile(profile_index):
                    if profile_index in profiles:
                        del profiles[profile_index]
                        refresh_profiles()

                # Function to add a new profile
                def add_profile():
                    new_index = max(profiles.keys(), default=-1) + 1  # Find the next available index
                    profiles[new_index] = {
                        'SP': '',
                        'ocpp_version': ''
                    }
                    refresh_profiles()

                # Toggle profiles visibility based on the version in the combobox
                def toggle_profile():
                    if version_combobox.get() in ('v2.0.1', 'v2.0'):
                        refresh_profiles()  # Show profiles if the version matches
                    else:
                        # Clear profile-related widgets
                        for widget in scrollable_frame.grid_slaves():
                            if int(widget.grid_info()["row"]) > 6 and int(widget.grid_info()["row"]) != 999:  # Remove profile-specific rows only
                                widget.grid_forget()

                # Call toggle_profile whenever the combobox value changes
                version_combobox.bind("<<ComboboxSelected>>", lambda event: toggle_profile())

                # Initial state based on the default or provided version
                toggle_profile()


            # Save button
            def save_changes():
                new_name = name_entry.get()
                # Update element properties
                old_name = element_data['name']
                element_data['name'] = new_name

                if element_type == "client":
                    element_data['version'] = version_combobox.get()
                    element_data['SecProfile'] = sprofile_entry.get()
                    element_data['priority'] = list(map(int, scrollable_frame.grid_slaves(row=7, column=1)[0].get().split(',')))
                    att = scrollable_frame.grid_slaves(row=8, column=1)[0].get()
                    element_data['attempts'] = int(att) if att.isdigit() else att
                    element_data['wait'] = scrollable_frame.grid_slaves(row=9, column=1)[0].get()
                    if version_combobox.get() in ('v2.0.1', 'v2.0'):
                        # Save profiles as a dictionary
                        saved_profiles = {}
                        for i, profile in profiles.items():
                            sp_value = scrollable_frame.grid_slaves(row=11 + int(i) * 5, column=1)[0].get()
                            ocpp_value = scrollable_frame.grid_slaves(row=12 + int(i) * 5, column=1)[0].get() 

                            # Update the profile dictionary
                            saved_profiles[i] = {
                                'SP': int(sp_value) if sp_value.isdigit() else sp_value,  
                                'ocpp_version': ocpp_value
                            }

                        element_data['profiles'] = saved_profiles
                elif element_type == "server":
                    element_data['multiple'] = int(multiple_entry.get())
            
                if element_type in ('client', 'server'):
                    if include_url_dns_var.get():
                        element_data['url'] = url_entry.get()
                        element_data['dns'] = dns_entry.get()
                    else:
                        element_data.pop('url', None)
                        element_data.pop('dns', None)

                # Update the element on the canvas
                icon, label, connections = self.elements[self.selected_element]
                self.itemconfig(icon, tags=new_name)
                self.itemconfig(label, tags=new_name, text = new_name)

                if 'links' in config.keys():
                    newL = []
                    for orig, dest in config['links']:
                        if orig == old_name:
                            newL.append([new_name, dest])
                        elif dest == old_name:
                            newL.append([orig, new_name])
                        else:
                            newL.append([orig, dest])
                    config['links'] = newL

                # Update element dictionary to use the new key
                self.elements[new_name] = self.elements.pop(self.selected_element)

                # Also update connections in self.elements to point to the new key
                for el in self.elements:
                    newC = []
                    if el != new_name:
                        for con in self.elements[el][2]:
                            num, elem = con
                            if elem == old_name:
                                newC.append((num, new_name))
                            else:
                                newC.append((num, elem))
                        self.elements[el][2].pop()
                        lst = list(self.elements[el])
                        lst[2] = newC
                        self.elements[el] = tuple(lst)


                # Update the selected element to the new name
                self.selected_element = new_name

                # Close the dialog
                dialog.destroy()

            save_button = tk.Button(scrollable_frame, text="Save", command=save_changes)
            save_button.grid(row=999, column=0, columnspan=2, pady=10)

            dialog.mainloop()


    def show_context_menu(self, event):
        """Show the context menu when right-clicking an element"""
        canvas_x = self.canvasx(event.x) 
        canvas_y = self.canvasy(event.y) 
        overlapping_items = self.find_overlapping(canvas_x, canvas_y, canvas_x, canvas_y)

        if len(overlapping_items) > 0:
            for element in self.elements:
                if self.elements[element][0]==overlapping_items[0]:
                    self.selected_element = element  # Store the name of the selected element   
                    self.context_menu.post(event.x_root, event.y_root)

    def toggle_connect_mode(self):
        """Enable or disable connection mode"""
        self.connect_mode = not self.connect_mode
        if self.connect_mode:
            messagebox.showinfo("Connect Mode", "Select two elements to connect.")
        else:
            self.start_element = None
    
    def zoom(self, scale_factor, center_x=None, center_y=None):
        """Zoom in or out on the canvas, scaling elements and connections."""
        # Get the center point for zoom (optional, defaults to canvas center)
        if center_x is None or center_y is None:
            center_x = self.canvasx(self.winfo_width() // 2)
            center_y = self.canvasy(self.winfo_height() // 2)
        
        # Scale all elements around the center point
        for element in self.elements:
            icon, label, connections = self.elements[element]
            
            # Get current coordinates
            icon_coords = self.coords(icon)
            
            # Calculate new positions relative to the zoom center
            new_icon_coords = [
                center_x + (x - center_x) * scale_factor for x in icon_coords
            ]
            
            # Move and scale the icon
            self.coords(icon, new_icon_coords)
            self.scale(icon, center_x, center_y, scale_factor, scale_factor)  # Scale icon size
            
            # Get new icon bounding box to position label below
            bbox = self.bbox(icon)  # Get the bounding box of the icon after scaling
            icon_x = (bbox[0] + bbox[2]) / 2  # Midpoint X of the icon
            icon_bottom_y = bbox[3]  # Bottom Y of the icon
            
            # Move label to stay under the icon
            label_x = icon_x
            label_y = icon_bottom_y + 10 * scale_factor  # Add padding (adjustable) below icon
            
            self.coords(label, label_x, label_y)
            
            # Update connections (if needed)
            for line, other_element in connections:
                self.update_connection_position(line, element, other_element)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Drag and Drop Network Editor")

        self.canvas = DragDropCanvas(self)

        # Buttons to add or remove elements
        self.add_client_button = tk.Button(self, text="Add Client", command=self.add_client)
        self.add_client_button.pack(side="left")

        self.add_server_button = tk.Button(self, text="Add Server", command=self.add_server)
        self.add_server_button.pack(side="left")

        self.add_router_button = tk.Button(self, text="Add Router", command=self.add_router)
        self.add_router_button.pack(side="left")

        self.add_router_button = tk.Button(self, text="Add Switch", command=self.add_switch)
        self.add_router_button.pack(side="left")

        self.add_router_button = tk.Button(self, text="Add Host", command=self.add_host)
        self.add_router_button.pack(side="left")

        self.add_router_button = tk.Button(self, text="Add DNS", command=self.add_dns)
        self.add_router_button.pack(side="left")

        self.connect_button = tk.Button(self, text="Connect Elements", command=self.canvas.toggle_connect_mode)
        self.connect_button.pack(side="left")

        self.zoom_in_button = tk.Button(self, text="Zoom In", command=lambda: self.canvas.zoom(scale_factor=1.1))
        self.zoom_in_button.pack(side="left")

        self.zoom_out_button = tk.Button(self, text="Zoom Out", command=lambda: self.canvas.zoom(scale_factor=0.9))
        self.zoom_out_button.pack(side="left")

        # Handle window close event to print YAML
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def add_router(self):
        """Add a new router"""
        name = f"router{len(config['routers'])+1}"
        config['routers'][name] = {'name': name}
        self.canvas.add_element(name, "router", 100, 100)


    def add_client(self):
        """Add a new client"""
        if 'clients' not in config.keys():
            config['clients'] = {}
        name = f"CLI{len(config['clients'])+1}"
        config['clients'][name] = {'name': name}
        self.canvas.add_element(name, "client", 50, 50)

    def add_server(self):
        """Add a new server"""
        if 'servers' not in config.keys():
            config['servers'] = {}
        name = f"server{len(config['servers'])+1}"
        config['servers'][name] = {'name': name}
        self.canvas.add_element(name, "server", 200, 50)
    
    def add_switch(self):
        """Add a new switch"""
        if 'switches' not in config.keys():
            config['switches'] = {}
        name = f"switch{len(config['switches'])+1}"
        config['switches'][name] = {'name': name}
        self.canvas.add_element(name, "switch", 200, 50)

    def add_dns(self):
        """Add a new DNS"""
        if 'dns' not in config.keys():
            config['dns'] = {}
        name = f"DNS{len(config['dns'])+1}"
        config['dns'][name] = {'name': name}
        self.canvas.add_element(name, "dns", 200, 50)
    
    def add_host(self):
        """Add a new host"""
        if 'hosts' not in config.keys():
            config['hosts'] = {}
        name = f"H{len(config['hosts'])+1}"
        config['hosts'][name] = {'name': name}
        self.canvas.add_element(name, "host", 200, 50)

    def on_close(self):
        """Print the final YAML when closing the window"""
        with open('charging/ipmininet/topologies/customTopo_config.yaml', 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
        self.destroy()

if __name__ == "__main__":
    app = App()

    # Pre-load elements from YAML configuration
    if 'clients' in config.keys():
        try:
            i=0
            for client_name in config['clients']:
                app.canvas.add_element(config['clients'][client_name]['name'], "client", 50, 50+i*50)
                i+=2
        except TypeError:
            print('No CP to configure')

    if 'servers' in config.keys():
        try:
            i=0
            for server_name in config.get('servers', {}):
                app.canvas.add_element(config['servers'][server_name]['name'], "server", 150, 50+i*50)
                i+=2
        except TypeError:
            print('No server to configure')

    if 'routers' in config.keys():
        try:
            i=0
            for router_name in config.get('routers', {}):
                app.canvas.add_element(config['routers'][router_name]['name'], "router", 250, 50+i*50)
                i+=2
        except TypeError:
            print('No router to configure')

    if 'switches' in config.keys():
        try:
            i=0
            for switch_name in config.get('switches', {}):
                app.canvas.add_element(config['switches'][switch_name]['name'], "switch", 350, 50+i*50)
                i+=2
        except TypeError:
            print('No switch to configure')
        
    if 'dns' in config.keys():
        try:
            i=0
            for dns_name in config.get('dns', {}):
                app.canvas.add_element(config['dns'][dns_name]['name'], "dns", 450, 50+i*50)
                i+=2
        except TypeError:
            print('No dns to configure')

    if 'hosts' in config.keys():
        try:
            i=0
            for host_name in config.get('hosts', {}):
                app.canvas.add_element(config['hosts'][host_name]['name'], "host", 550, 50+i*50)
                i+=2
        except TypeError:
            print('No host to configure')
            
    if 'links' in config.keys():
        try:
            for link in config['links']:
                source_name = link[0]
                target_name = link[1]
                app.canvas.add_connection(source_name, target_name, start= False)
        except TypeError:
            print('No link to configure')

    app.mainloop()
