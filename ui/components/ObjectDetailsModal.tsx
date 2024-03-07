// ObjectDetailsSection.tsx

import React from 'react';
import {Detail} from "./TableData";
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';

interface ObjectDetailsSectionProps {
    objectDetails: Detail[];
    handleDetailChange: (index: number, key: number, value: any) => void;
    currentDetail: Detail;
    setCurrentDetail: (detail: Detail) => void;
    addDetail: () => void;
    onClose: () => void;
}

const ObjectDetailsSection: React.FC<ObjectDetailsSectionProps> = ({
    objectDetails,
    handleDetailChange,
    currentDetail,
    setCurrentDetail,
    addDetail,
    onClose
}) => {
    const inputStyle: React.CSSProperties = {
        padding: '5px',
        margin: '5px 0',
        border: '1px solid #ccc',
        borderRadius: '4px',
        width: 'calc(50% - 10px)',
    };

    const detailBoxStyle: React.CSSProperties = {
    border: '1px solid gray',
    borderRadius: '5px',
    padding: '10px',
    margin: '10px 0',
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between'
};

    return (
        <div style={{flex: 1, padding: '20px', borderLeft: '1px solid gray', overflowY: 'auto'}}>
            <IconButton style={{position: 'absolute', right: '20px', top: '20px'}} onClick={onClose}>
                <CloseIcon/>
            </IconButton>

            <h2>Object Details</h2>

            {objectDetails?.map((detail: Detail, index: number) => (
                <div key={index} style={detailBoxStyle}>
                    <input
                        style={inputStyle}
                        value={detail[0]}
                        placeholder="Detail name"
                        onChange={(e) => handleDetailChange(index, 0, e.target.value)}
                    />
                    <input
                        style={inputStyle}
                        type="number"
                        value={detail[1]}
                        placeholder="Detail value"
                        onChange={(e) => handleDetailChange(index, 1, e.target.value)}
                    />
                </div>
            ))}
            <h3>Add New Detail</h3>
            <div style={detailBoxStyle}>
                <input
                    style={inputStyle}
                    value={currentDetail[0]}
                    placeholder="Detail name"
                    onChange={(e) => setCurrentDetail([e.target.value, currentDetail[1]])}
                />
                <input
                    style={inputStyle}
                    type="number"
                    value={currentDetail[1]}
                    placeholder="Detail value"
                    onChange={(e) => setCurrentDetail([currentDetail[0], e.target.valueAsNumber])}
                />
                <button type={"submit"} onClick={addDetail}>Add</button>
            </div>
        </div>
    );
}

export default ObjectDetailsSection;
