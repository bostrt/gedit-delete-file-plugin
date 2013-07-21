from gi.repository import GObject, Gtk, Gedit
from gi._glib import GError

ui_str = """
<ui>
  <menubar name="MenuBar">
    <menu name="FileMenu" action="File">
      <placeholder name="FileOps_4">
        <menuitem name="DeleteFile" action="DeleteFile"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""

class Test(GObject.Object, Gedit.WindowActivatable):
      __gtype_name = "Testing"
      window = GObject.property(type=Gedit.Window)

      def __init__(self):
          GObject.Object.__init__(self)
          self._tab_change_handler_id = None
          self._tab_state_change_handler_id = None

      def do_activate(self):
            self._insert_menu_item()
            # Listen for tab changes.
            self.tab_change_handler_id = self.window.connect(
                  'active-tab-changed', self._tab_change)
            self._tab_state_change_handler_id = self.window.connect(
                  'active-tab-state-changed', self._tab_state_change)

      def do_deactivate(self):
            # Clean up connected signals
            if self._tab_change_handler_id is not None:
                  self.window.disconnect(self._tab_change_handler_id)
            if self._tab_state_change_handler_id is not None:
                  self.window.disconnect(self._tab_state_change_handler_id)

      def _tab_change(self, window, tab):
            self._update_menu_item(window, tab)

      def _tab_state_change(self, window):
            self._update_menu_item(window, window.get_active_tab())

      def _update_menu_item(self, window, tab):
            active_tab =  window.get_active_tab()
            ro = active_tab.get_document().get_readonly()
            item =  window.get_ui_manager().get_widget(
                  '/ui/MenuBar/FileMenu/FileOps_4/DeleteFile')
            item.set_sensitive(not ro)
            print ro

      def _insert_menu_item(self):
            manager = self.window.get_ui_manager()
            self._action_group = Gtk.ActionGroup('DeleteFilePluginAction')
            self._action_group.add_actions([('DeleteFile', None, _('Delete File'),
                                             None, _('Delete File'),
                                             self.on_delete_file_action)])
            manager.insert_action_group(self._action_group, -1)
            self._ui_id = manager.add_ui_from_string(ui_str)
      
      def on_delete_file_action(self, action):
            active_tab = self.window.get_active_tab()
            active_doc = active_tab.get_document()

            confirm = Gtk.MessageDialog(
                  self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.QUESTION, 
                  Gtk.ButtonsType.OK_CANCEL,
                  _('Are you sure you want to delete %s?' % active_doc.get_short_name_for_display()))
            
            response = confirm.run()
            confirm.destroy()
            
            if response == Gtk.ResponseType.OK:
                  try:
                        location = active_doc.get_location()
                        if location is not None:
                              location.delete(None)
                              self.window.close_tab(active_tab)
                  except GError as e:
                        error = Gtk.MessageDialog(
                              self.window,
                              Gtk.DialogFlags.MODAL,
                              Gtk.MessageType.WARNING,
                              Gtk.ButtonsType.OK,
                              _(e.message))
                        error.run()
                        error.destroy()
            
