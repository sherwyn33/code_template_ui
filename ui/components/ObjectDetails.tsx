import React, {useState, useContext} from 'react';
import {Table, TableRow, TableCell, Button, Modal, Backdrop, Fade, Collapse, IconButton} from '@material-ui/core';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import ExpandLessIcon from '@material-ui/icons/ExpandLess';
import DataContext from "../DataContext";
import mockTableData, {Detail, TableData, TableDataEntry, Template} from "./TableData";
import {Paper, TableBody, TableHead} from "material-ui-core";
import FileContentModal from "./FileContentModal";
import ControlPanel from "./ControlPanel";

const ObjectDetails: React.FC = () => {
    let contextValue = useContext(DataContext);
    if (contextValue?.data?.length == 0) {
        console.log("context doesn't work")
        contextValue.data = mockTableData; // or some error message or component
    }
    const {data: tableData} = contextValue;

    const [fileContent, setFileContent] = useState<string | null>(null);
    const [isFileModalOpen, setFileModalOpen] = useState(false);
    const [objectDetails, setObjectDetails] = useState<any>(null);
    const [detailId, setDetailId] = useState<number>(null);
    const [expandedRows, setExpandedRows] = useState<string[]>([]);  // to keep track of expanded rows by filePath
    const [currentDetail, setCurrentDetail] = useState<Detail>(["", 0]); // Temp state for new detail form
    const [linkedIdUpdates, setLinkedIdUpdates] = useState({});
    const [templates, setTemplates] = useState<{ [id: number]: Template }>({});
    const [selectedRow, setSelectedRow] = useState<{ type: 'main' | 'connected', id: number, connectedIndex?: number } | null>(null);


    const handleFileClick = async (detail: Detail[], filePath: string, detailId: number) => {
        try {
            const response = await fetch(`/api/object_details/file_content?file_path=${filePath}`);
            const data = await response.json();
            if (data.content) {
                setFileContent(data.content);
                setFileModalOpen(true);
                setObjectDetails(detail);
                setDetailId(detailId);
            }
        } catch (error) {
            console.error("Error loading file content:", error);
        }
    }


    const handleTemplateRequest = async (linkedId: number) => {
        try {
            const sliceOfTableData = tableData.filter(data => data.linkedId === linkedId);
            const response = await fetch('/api/object_details/template', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({table_data: sliceOfTableData}),
            });
            const data = await response.json();
            if (data.templates) {
                setTemplates(prev => ({...prev, [linkedId]: data.templates}));
            }
        } catch (error) {
            console.error("Error loading template data:", error);
        }
    }

    function onViewTemplateClick() {
        if (selectedRow) {
            if (selectedRow.type === 'main') {
                const template = templates[selectedRow.id];
                if (template) {
                    setFileContent(template.all_main_file_paths_output);
                }
            } else if (selectedRow.type === 'connected' && typeof selectedRow.connectedIndex !== 'undefined') {
                const template = templates[selectedRow.id];
                if (template && template.individual_outputs[selectedRow.connectedIndex]) {
                    setFileContent(template.individual_outputs[selectedRow.connectedIndex]);
                }
            }
            setFileModalOpen(true);
        }
    }

// Ensure to call onFileContentModalOpen() when setting setFileModalOpen(true)


    const handleDetailChange = (index: number, key: number, value: any) => {
        const updatedDetails = [...objectDetails];
        updatedDetails[index][key] = value;
        setObjectDetails(updatedDetails);
    };

    const addDetail = () => {
        setObjectDetails(prev => [...prev, currentDetail]);
        setCurrentDetail(["", 0]); // Reset the form
    };

    const toggleRowExpansion = (filePath: string) => {
        if (expandedRows.includes(filePath)) {
            setExpandedRows(prev => prev.filter(path => path !== filePath));
        } else {
            setExpandedRows(prev => [...prev, filePath]);
        }
    }


    function onFileContentModalClose() {
        if (detailId) {
            tableData.forEach(node => {
                if (node.id === detailId) {
                    node.details = objectDetails
                }
            });
        }
        setDetailId(null);
        setFileModalOpen(false);
    }

    let previousLinkedId = -1;
    let alternateGroup = false;

    const sortedTableData = [...tableData].sort((a, b) => a.linkedId - b.linkedId);
    const handleSave = () => {
        // Apply the updates to tableData
        tableData.forEach(row => {
            if (linkedIdUpdates[row.id] !== undefined) {
                row.linkedId = linkedIdUpdates[row.id];
            }
        });

        // Clear the updates
        setLinkedIdUpdates({});

        // Call your API to save the updated tableData
        // updateTableDataAPI(tableData);
    }
    return (

        <div style={{margin: '20px'}}>
            <div style={{margin: '20px'}}>
                <ControlPanel
                    onSave={handleSave}
                />
            </div>
            <Paper style={{overflow: 'hidden'}}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell></TableCell>
                            <TableCell>#</TableCell>
                            <TableCell>Group #</TableCell>
                            <TableCell>File Name</TableCell>
                            <TableCell>Object #</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {sortedTableData.map((row) => {
                            const isNewGroup = previousLinkedId !== row.linkedId;
                            const groupStyle = isNewGroup ? {borderTop: '2px solid #f5f5f5'} : {};

                            if (isNewGroup) {
                                alternateGroup = !alternateGroup;
                                previousLinkedId = row.linkedId;
                            }
                            const backgroundStyle = alternateGroup ? {backgroundColor: '#fafafa'} : {};

                            return (
                                <React.Fragment key={row.id + row.file.file_path}>
                                    <TableRow style={{...groupStyle, ...backgroundStyle}}>
                                        <TableCell>
                                            <IconButton size="small"
                                                        onClick={() => toggleRowExpansion(row.file.file_path)}>
                                                {expandedRows.includes(row.file.file_path) ? <ExpandLessIcon/> :
                                                    <ExpandMoreIcon/>}
                                            </IconButton>
                                        </TableCell>
                                        <TableCell>
                                            {row.id}
                                        </TableCell>
                                        <TableCell>
                                            <input
                                                type="number"
                                                value={linkedIdUpdates[row.id] || row.linkedId}
                                                onChange={(e) => {
                                                    const value = e.target.value;
                                                    setLinkedIdUpdates(prev => ({...prev, [row.id]: parseInt(value)}));
                                                }}
                                            />
                                        </TableCell>

                                        <TableCell>
                                            <Button
                                                onClick={() => handleFileClick(row.details, row.file.file_path, row.id)}>
                                                {row.file.file_path.split('\\').pop()}
                                            </Button>
                                        </TableCell>
                                        <TableCell>
                                            {row?.details?.length}
                                        </TableCell>
                                        <TableCell>
                                            <Button onClick={() => handleTemplateRequest(row.linkedId)}>Fetch
                                                Template</Button>
                                        </TableCell>
                                        <TableCell>
                                            <Button
                                                onClick={() => {
                                                                                                        setSelectedRow({type: 'main', id: row.linkedId});

                                                                                                        onViewTemplateClick();
                                                }}
                                            >
                                                View Template
                                            </Button>
                                        </TableCell>

                                    </TableRow>
                                    <TableRow>
                                        <TableCell style={{paddingBottom: 0, paddingTop: 0}} colSpan={8}>
                                            <Collapse in={expandedRows.includes(row.file.file_path)} timeout="auto"
                                                      unmountOnExit>
                                                <Table size="small">
                                                    <tbody>
                                                    {row?.file?.connected_files?.map((connectedFile) => (
                                                        <TableRow key={row.id + connectedFile.file_path}
                                                                  style={backgroundStyle}>
                                                            <TableCell></TableCell>
                                                            <TableCell></TableCell>
                                                            <TableCell></TableCell>
                                                            <TableCell></TableCell>
                                                            <TableCell>
                                                                <Button
                                                                    onClick={() => handleFileClick(row.details, connectedFile.file_path, row.linkedId)}>
                                                                    {connectedFile.file_path.split('\\').pop()}
                                                                </Button>
                                                            </TableCell>
                                                            <TableCell></TableCell>
                                                            <TableCell></TableCell>
                                                            <TableCell>
                                                                <Button
                                                                    onClick={() => {
                                                                        setSelectedRow({
                                                                            type: 'connected',
                                                                            id: row.id,
                                                                            connectedIndex: row.file.connected_files.indexOf(connectedFile)
                                                                        });
                                                                        onViewTemplateClick();
                                                                    }}
                                                                >
                                                                    View Template
                                                                </Button>
                                                            </TableCell>
                                                        </TableRow>
                                                    ))}
                                                    </tbody>
                                                </Table>
                                            </Collapse>
                                        </TableCell>
                                    </TableRow>
                                </React.Fragment>
                            );
                        })}
                    </TableBody>
                </Table>
            </Paper>

            <FileContentModal
                isOpen={isFileModalOpen}
                onClose={() => onFileContentModalClose()}
                content={fileContent}
                objectDetails={objectDetails}
                handleDetailChange={handleDetailChange}
                currentDetail={currentDetail}
                setCurrentDetail={setCurrentDetail}
                addDetail={addDetail}
            />
        </div>
    );
}

export default ObjectDetails;
