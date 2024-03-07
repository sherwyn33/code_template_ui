import React from 'react';

interface ControlPanelProps {
    onSave: () => void;
}

const ControlPanel: React.FC<ControlPanelProps> = ({ onSave }) => {
    return (
        <div style={{ padding: '10px', border: '1px solid #ccc', marginBottom: '20px' }}>
            <button onClick={onSave}>Save Changes</button>
        </div>
    );
};

export default ControlPanel;
