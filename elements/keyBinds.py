import pygame
#key binds for navigation only, other key events are handled in the elements themselves

class KeyBinds:
    @staticmethod
    def vertical(event, panel, current):
        selectable = panel.get_selectable_children()
        if current not in selectable:
            return selectable[0] if selectable else current
        idx = selectable.index(current)
        n = len(selectable)
        if event.key == pygame.K_DOWN:
            if idx + 1 < n:
                return selectable[idx + 1]
            else:
                # At end, try to move to neighbor panel (down)
                neighbor = panel.get_neighbor('down') if hasattr(panel, 'get_neighbor') else None
                if neighbor:
                    neighbor_selectable = neighbor.get_selectable_children()
                    return neighbor_selectable[0] if neighbor_selectable else current
        elif event.key == pygame.K_UP:
            if idx - 1 >= 0:
                return selectable[idx - 1]
            else:
                # At start, try to move to neighbor panel (up)
                neighbor = panel.get_neighbor('up') if hasattr(panel, 'get_neighbor') else None
                if neighbor:
                    neighbor_selectable = neighbor.get_selectable_children()
                    return neighbor_selectable[0] if neighbor_selectable else current
        # Also handle left/right for neighbor panels
        if event.key == pygame.K_RIGHT:
            neighbor = panel.get_neighbor('right') if hasattr(panel, 'get_neighbor') else None
            if neighbor:
                neighbor_selectable = neighbor.get_selectable_children()
                return neighbor_selectable[0] if neighbor_selectable else current
        elif event.key == pygame.K_LEFT:
            neighbor = panel.get_neighbor('left') if hasattr(panel, 'get_neighbor') else None
            if neighbor:
                neighbor_selectable = neighbor.get_selectable_children()
                return neighbor_selectable[0] if neighbor_selectable else current
        return current

    @staticmethod
    def horizontal(event, panel, current):
        selectable = panel.get_selectable_children()
        if current not in selectable:
            return selectable[0] if selectable else current
        idx = selectable.index(current)
        n = len(selectable)
        if event.key == pygame.K_RIGHT:
            if idx + 1 < n:
                return selectable[idx + 1]
            else:
                # At end, try to move to neighbor panel (right)
                neighbor = panel.get_neighbor('right') if hasattr(panel, 'get_neighbor') else None
                if neighbor:
                    neighbor_selectable = neighbor.get_selectable_children()
                    return neighbor_selectable[0] if neighbor_selectable else current
        elif event.key == pygame.K_LEFT:
            if idx - 1 >= 0:
                return selectable[idx - 1]
            else:
                # At start, try to move to neighbor panel (left)
                neighbor = panel.get_neighbor('left') if hasattr(panel, 'get_neighbor') else None
                if neighbor:
                    neighbor_selectable = neighbor.get_selectable_children()
                    return neighbor_selectable[-1] if neighbor_selectable else current
                
        # Also handle up/down for neighbor panels
        if event.key == pygame.K_DOWN:
            # try to move to neighbor panel (down)
            neighbor = panel.get_neighbor('down') if hasattr(panel, 'get_neighbor') else None
            if neighbor:
                neighbor_selectable = neighbor.get_selectable_children()
                return neighbor_selectable[0] if neighbor_selectable else current
        elif event.key == pygame.K_UP:
            # try to move to neighbor panel (up)
            neighbor = panel.get_neighbor('up') if hasattr(panel, 'get_neighbor') else None
            if neighbor:
                neighbor_selectable = neighbor.get_selectable_children()
                return neighbor_selectable[-1] if neighbor_selectable else current
        return current
    
    @staticmethod
    def table(event, panel, current):
        selectable = panel.get_selectable_children()
        if not selectable:
            return current
            
        # Get current position in the table
        if current not in selectable:
            return selectable[0]
            
        idx = selectable.index(current)
        cols = panel.cols
        rows = len(panel._data) if hasattr(panel, '_data') else 0
        
        # Calculate current row and column
        current_row = idx // cols
        current_col = idx % cols
        
        # Handle navigation
        if event.key == pygame.K_RIGHT:
            # Move right within row
            if current_col + 1 < cols and idx + 1 < len(selectable):
                return selectable[idx + 1]
            else:
                # At end of row, try to move to neighbor panel (right)
                neighbor = panel.get_neighbor('right') if hasattr(panel, 'get_neighbor') else None
                if neighbor:
                    neighbor_selectable = neighbor.get_selectable_children()
                    return neighbor_selectable[0] if neighbor_selectable else current
        elif event.key == pygame.K_LEFT:
            # Move left within row
            if current_col > 0:
                return selectable[idx - 1]
            else:
                # At start of row, try to move to neighbor panel (left)
                neighbor = panel.get_neighbor('left') if hasattr(panel, 'get_neighbor') else None
                if neighbor:
                    neighbor_selectable = neighbor.get_selectable_children()
                    return neighbor_selectable[0] if neighbor_selectable else current
        elif event.key == pygame.K_DOWN:
            # Move down to same column in next row
            next_row = current_row + 1
            next_idx = next_row * cols + current_col
            if next_row < rows and next_idx < len(selectable):
                return selectable[next_idx]
            else:
                # At last row, try to move to neighbor panel (down)
                neighbor = panel.get_neighbor('down') if hasattr(panel, 'get_neighbor') else None
                if neighbor:
                    neighbor_selectable = neighbor.get_selectable_children()
                    return neighbor_selectable[0] if neighbor_selectable else current
        elif event.key == pygame.K_UP:
            # Move up to same column in previous row
            prev_row = current_row - 1
            if prev_row >= 0:
                prev_idx = prev_row * cols + current_col
                if prev_idx < len(selectable):
                    return selectable[prev_idx]
            else:
                # At first row, try to move to neighbor panel (up)
                neighbor = panel.get_neighbor('up') if hasattr(panel, 'get_neighbor') else None
                if neighbor:
                    neighbor_selectable = neighbor.get_selectable_children()
                    return neighbor_selectable[0] if neighbor_selectable else current
        # Wrap-around navigation (optional)
        elif event.key == pygame.K_TAB:
            # Move to next cell with wrap-around
            next_idx = (idx + 1) % len(selectable)
            return selectable[next_idx]
        elif event.key == pygame.K_TAB and pygame.key.get_mods() & pygame.KMOD_SHIFT:
            # Move to previous cell with wrap-around
            prev_idx = (idx - 1) % len(selectable)
            return selectable[prev_idx]
        
        return current

    @staticmethod
    def global_keys(event, current, running_flag):
        if event.key == pygame.K_ESCAPE:
            if current.parent:
                current = current.focus_parent()
        elif event.key == pygame.K_RETURN:
            if current.parent:
                current = current.focus_child()
        elif event.key == pygame.K_q:
            print("Exiting.")
            running_flag[0] = False
        return current, running_flag

    layout_map = {
        "vertical": vertical.__func__,
        "horizontal": horizontal.__func__,
        "table": table.__func__,
    }