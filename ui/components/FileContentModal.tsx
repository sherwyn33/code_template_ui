import React from 'react';
import {Modal, Backdrop, Fade, IconButton} from '@material-ui/core';
import CloseIcon from '@material-ui/icons/Close';
import {Detail} from "./TableData";
import ObjectDetailsSection from "./ObjectDetailsModal";

interface FileContentModalProps {
    isOpen: boolean;
    onClose: () => void;
    content: string;
    objectDetails: Detail[];  // Assuming Detail type has been imported
    handleDetailChange: (index: number, key: number, value: any) => void;
    currentDetail: Detail;
    setCurrentDetail: (detail: Detail) => void;
    addDetail: () => void;
}

const modalStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'fixed', // change to fixed
    top: '0',
    left: '0',
    right: '0',
    bottom: '0',
    backgroundColor: 'white',
    overflow: 'hidden',
    flexDirection: 'row',
};

const FileContentModal: React.FC<FileContentModalProps> = ({
                                                               isOpen,
                                                               onClose,
                                                               content,
                                                               objectDetails,
                                                               handleDetailChange,
                                                               currentDetail,
                                                               setCurrentDetail,
                                                               addDetail,
                                                           }) => {
    const highlightedContent = (): { __html: string } => {
        if (!content || !objectDetails) return {__html: content || ''};

        let modifiedContent = content;

        objectDetails.forEach(detail => {
            const word = detail[0];
            if (word) {
                const regex = new RegExp(`(${word})`, 'gi');
                modifiedContent = modifiedContent.replace(regex, '<mark>$1</mark>');
            }
        });

        modifiedContent = modifiedContent.replace(/\n/g, '<br />');
        modifiedContent = modifiedContent.replace(/\t/g, '   ');

        return {__html: modifiedContent};
    };


     return (
        <Modal
            open={isOpen}
            onClose={onClose}
            closeAfterTransition
            BackdropComponent={Backdrop}
            style={modalStyle}
        >
            <Fade in={isOpen}>
                <div style={{width: '100%', height: '100%', display: 'flex', flexDirection: 'row'}}>
                    {/* Content section */}
                    <div
                        style={{flex: 2, padding: '20px', overflowY: 'auto'}}
                        dangerouslySetInnerHTML={highlightedContent()}
                    ></div>

                    {/* Object Details section */}
                        <ObjectDetailsSection
                            objectDetails={objectDetails}
                            handleDetailChange={handleDetailChange}
                            currentDetail={currentDetail}
                            setCurrentDetail={setCurrentDetail}
                            addDetail={addDetail}
                            onClose={onClose}
                        />
                </div>
            </Fade>
        </Modal>
    );
};

export default FileContentModal;
