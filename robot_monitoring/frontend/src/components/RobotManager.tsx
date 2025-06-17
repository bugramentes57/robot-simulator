import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Fab,
  Tooltip,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";

interface RobotManagerProps {
  onRobotChange: () => void;
}

const RobotManager: React.FC<RobotManagerProps> = ({ onRobotChange }) => {
  const [open, setOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [selectedRobot, setSelectedRobot] = useState<{
    robot_id: string;
    description: string;
  } | null>(null);
  const [newRobotId, setNewRobotId] = useState("");
  const [description, setDescription] = useState("");
  const [activeRobots, setActiveRobots] = useState<
    Array<{ robot_id: string; description: string }>
  >([]);

  const getCookie = (name: string): string | null => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(";").shift() || null;
    return null;
  };

  const handleAddRobot = async () => {
    try {
      const csrfToken = getCookie("csrftoken");

      const response = await fetch("http://localhost:8000/api/robots/add/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken || "",
        },
        credentials: "include",
        body: JSON.stringify({ robot_id: newRobotId, description }),
      });

      if (response.ok) {
        setNewRobotId("");
        setDescription("");
        fetchRobots();
        onRobotChange();
      } else {
        const errorData = await response.json();
        console.error("Robot eklenemedi:", errorData);
      }
    } catch (error) {
      console.error("Robot eklenirken hata:", error);
    }
  };

  const handleRemoveRobot = async (robotId: string) => {
    try {
      const csrfToken = getCookie("csrftoken");

      const response = await fetch(
        `http://localhost:8000/api/robots/${robotId}`,
        {
          method: "DELETE",
          headers: {
            "X-CSRFToken": csrfToken || "",
          },
          credentials: "include",
        }
      );

      if (response.ok) {
        fetchRobots();
        onRobotChange();
      }
    } catch (error) {
      console.error("Robot silinirken hata:", error);
    }
  };

  const fetchRobots = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/robots/");
      const data = await response.json();
      setActiveRobots(data);
    } catch (error) {
      console.error("Robotlar alınırken hata:", error);
    }
  };

  const handleEditRobot = async () => {
    try {
      const csrfToken = getCookie("csrftoken");

      const response = await fetch(
        `http://localhost:8000/api/robots/${selectedRobot?.robot_id}/`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken || "",
          },
          credentials: "include",
          body: JSON.stringify({
            robot_id: selectedRobot?.robot_id,
            description: description,
          }),
        }
      );

      if (response.ok) {
        setEditMode(false);
        setSelectedRobot(null);
        setDescription("");
        fetchRobots();
        onRobotChange();
      } else {
        const errorData = await response.json();
        console.error("Robot düzenlenemedi:", errorData);
      }
    } catch (error) {
      console.error("Robot düzenlenirken hata:", error);
    }
  };

  const startEdit = (robot: { robot_id: string; description: string }) => {
    setSelectedRobot(robot);
    setDescription(robot.description);
    setEditMode(true);
    setOpen(true);
  };

  return (
    <>
      <Tooltip title="Robot Ekle">
        <Fab
          color="primary"
          onClick={() => {
            setEditMode(false);
            setSelectedRobot(null);
            setDescription("");
            setNewRobotId("");
            setOpen(true);
          }}
          sx={{ position: "fixed", bottom: 16, right: 16 }}
        >
          <AddIcon />
        </Fab>
      </Tooltip>

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>
          {editMode ? "Robot Düzenle" : "Robot Yönetimi"}
        </DialogTitle>
        <DialogContent>
          {!editMode && (
            <TextField
              autoFocus
              margin="dense"
              label="Robot ID"
              fullWidth
              value={newRobotId}
              onChange={(e) => setNewRobotId(e.target.value)}
            />
          )}
          <TextField
            margin="dense"
            label="Açıklama"
            fullWidth
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          {!editMode && (
            <List>
              {activeRobots.map((robot) => (
                <ListItem key={robot.robot_id}>
                  <ListItemText
                    primary={robot.robot_id}
                    secondary={robot.description}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      onClick={() => startEdit(robot)}
                      sx={{ marginRight: 1 }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      edge="end"
                      onClick={() => handleRemoveRobot(robot.robot_id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>İptal</Button>
          {editMode ? (
            <Button onClick={handleEditRobot} disabled={!description}>
              Kaydet
            </Button>
          ) : (
            <Button onClick={handleAddRobot} disabled={!newRobotId}>
              Robot Ekle
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </>
  );
};

export default RobotManager;
