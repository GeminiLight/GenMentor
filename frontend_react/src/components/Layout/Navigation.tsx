import React, { useState } from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Divider,
  IconButton,
  Box,
  Tooltip,
  Collapse,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Route as RouteIcon,
  Insights as InsightsIcon,
  MenuBook as MenuBookIcon,
  Person as PersonIcon,
  Flag as FlagIcon,
  Settings as SettingsIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  ExpandLess as ExpandLessIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { NAVIGATION_ITEMS, ROUTES } from '../../config';

const DRAWER_WIDTH = 280;
const DRAWER_WIDTH_COLLAPSED = 72;

interface NavigationProps {
  open: boolean;
  onToggle: () => void;
}

const iconMap: Record<string, React.ElementType> = {
  dashboard: DashboardIcon,
  route: RouteIcon,
  insights: InsightsIcon,
  menu_book: MenuBookIcon,
  person: PersonIcon,
  flag: FlagIcon,
  settings: SettingsIcon,
};

const Navigation: React.FC<NavigationProps> = ({ open, onToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [expandedItems, setExpandedItems] = useState<Record<string, boolean>>({});

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  const handleToggleExpand = (itemId: string) => {
    setExpandedItems((prev) => ({
      ...prev,
      [itemId]: !prev[itemId],
    }));
  };

  const isActive = (path: string) => location.pathname === path;

  const renderNavItem = (item: any, depth: number = 0) => {
    const IconComponent = iconMap[item.icon] || DashboardIcon;
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedItems[item.id];

    return (
      <div key={item.id}>
        <ListItem disablePadding sx={{ display: 'block' }}>
          <Tooltip title={!open ? item.description : ''} placement="right" arrow>
            <ListItemButton
              onClick={() => {
                if (hasChildren) {
                  handleToggleExpand(item.id);
                } else {
                  handleNavigation(item.path);
                }
              }}
              selected={isActive(item.path)}
              sx={{
                minHeight: 48,
                justifyContent: open ? 'initial' : 'center',
                px: 2.5,
                mx: 1,
                borderRadius: 2,
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'primary.contrastText',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'primary.contrastText',
                  },
                },
                '&:hover': {
                  backgroundColor: 'action.hover',
                  borderRadius: 2,
                },
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: open ? 3 : 'auto',
                  justifyContent: 'center',
                  color: isActive(item.path) ? 'inherit' : 'text.secondary',
                }}
              >
                <IconComponent />
              </ListItemIcon>
              <ListItemText
                primary={item.label}
                sx={{
                  opacity: open ? 1 : 0,
                  '& .MuiTypography-root': {
                    fontWeight: isActive(item.path) ? 600 : 400,
                  },
                }}
              />
              {hasChildren && open && (
                isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />
              )}
            </ListItemButton>
          </Tooltip>
        </ListItem>
        
        {hasChildren && (
          <Collapse in={isExpanded && open} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children && item.children.map((child: any) => renderNavItem(child, depth + 1))}
            </List>
          </Collapse>
        )}
      </div>
    );
  };

  return (
    <Drawer
      variant="permanent"
      open={open}
      sx={{
        width: open ? DRAWER_WIDTH : DRAWER_WIDTH_COLLAPSED,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: open ? DRAWER_WIDTH : DRAWER_WIDTH_COLLAPSED,
          boxSizing: 'border-box',
          borderRight: '1px solid',
          borderColor: 'divider',
          backgroundColor: 'background.paper',
          transition: 'width 0.3s ease',
        },
      }}
    >
      <Toolbar
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: open ? 'space-between' : 'center',
          px: [1],
          minHeight: 64,
        }}
      >
        {open && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              ml: 1,
            }}
          >
            <Box
              component="img"
              src="/assets/avatar.png"
              alt="GenMentor"
              sx={{
                width: 32,
                height: 32,
                borderRadius: '50%',
                mr: 2,
              }}
            />
            <Box
              component="span"
              sx={{
                fontWeight: 600,
                fontSize: '1.25rem',
                color: 'primary.main',
              }}
            >
              GenMentor
            </Box>
          </Box>
        )}
        <IconButton onClick={onToggle} sx={{ color: 'text.secondary' }}>
          {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </IconButton>
      </Toolbar>
      
      <Divider />
      
      <List sx={{ px: 0.5, py: 1 }}>
        {NAVIGATION_ITEMS.map((item) => renderNavItem(item))}
      </List>
      
      <Divider sx={{ mt: 'auto' }} />
      
      <List sx={{ px: 0.5, py: 1 }}>
        <ListItem disablePadding sx={{ display: 'block' }}>
          <Tooltip title={!open ? 'Settings' : ''} placement="right" arrow>
            <ListItemButton
              onClick={() => handleNavigation(ROUTES.SETTINGS)}
              selected={isActive(ROUTES.SETTINGS)}
              sx={{
                minHeight: 48,
                justifyContent: open ? 'initial' : 'center',
                px: 2.5,
                mx: 1,
                borderRadius: 2,
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'primary.contrastText',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'primary.contrastText',
                  },
                },
                '&:hover': {
                  backgroundColor: 'action.hover',
                  borderRadius: 2,
                },
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: open ? 3 : 'auto',
                  justifyContent: 'center',
                  color: isActive(ROUTES.SETTINGS) ? 'inherit' : 'text.secondary',
                }}
              >
                <SettingsIcon />
              </ListItemIcon>
              <ListItemText
                primary="Settings"
                sx={{
                  opacity: open ? 1 : 0,
                  '& .MuiTypography-root': {
                    fontWeight: isActive(ROUTES.SETTINGS) ? 600 : 400,
                  },
                }}
              />
            </ListItemButton>
          </Tooltip>
        </ListItem>
      </List>
    </Drawer>
  );
};

export default Navigation;