import React from "react";
import { Snackbar } from "@mui/material";
import Alert from "@mui/material/Alert";
const Alert1 = ({open,handleClose}) => {
    return (
        <>
        <Snackbar
            open={open}
            autoHideDuration={2000}
            onClose={handleClose}
            anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
            >
                <Alert onClose={handleClose} variant="filled"  severity="error">
                Impossible de se conecter 
                </Alert>
            </Snackbar>  
        </>       
    )
}
export default Alert1;