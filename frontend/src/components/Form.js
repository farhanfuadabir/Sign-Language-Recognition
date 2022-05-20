import { useState } from "react";
import { Label, Input, Collapse } from "reactstrap";
import { Button } from "reactstrap";
import GestureSelector from "./GestureSelector";
import ProgressBar from "./ProgressBar";

const PROGRESS_UPDATE_INT = 100;
const PREPARATION_DURATION = 3000;
const RECORDING_DURATION = 5000;
const TOTAL_DURATION = PREPARATION_DURATION + RECORDING_DURATION;
// ... 0.002 is added to compensate for the ui update delay
const PROGRESS_INCREMENT = PROGRESS_UPDATE_INT / TOTAL_DURATION + 0.002;
const PREPARATION_UPDATE_COUNT = PREPARATION_DURATION / PROGRESS_UPDATE_INT;

var count = 0;

export default function Form({ onSubmit }) {
    const [subjectId, setSubjectId] = useState("");
    const [gesture, setGesture] = useState("");
    const [submitBtnColor, setSubmitBtnColor] = useState("primary");
    const [isRecording, setRecording] = useState(false);
    const [preparationProgress, setPreparationProgress] = useState(0);
    const [recordingProgress, setRecordingProgress] = useState(0);
    const [buttonText, setButtonText] = useState("Start Recording");

    const onSubmitClick = () => {
        console.log(isRecording);
        if (!isRecording) {
            setSubmitBtnColor("warning");
            setButtonText("Prepare to Perform the Gesture ... ");
            const timerId = setInterval(() => {
                if (count < PREPARATION_UPDATE_COUNT) {
                    setPreparationProgress(
                        (pProgress) => pProgress + PROGRESS_INCREMENT
                    );
                } else {
                    setRecordingProgress(
                        (rProgress) => rProgress + PROGRESS_INCREMENT
                    );
                }
                count++;
            }, PROGRESS_UPDATE_INT);

            setTimeout(() => {
                setSubmitBtnColor("danger");
                setButtonText("Perform the Gesture Now!");
            }, PREPARATION_DURATION);

            setTimeout(() => {
                onSubmit(RECORDING_DURATION, subjectId, gesture);
                setSubmitBtnColor("primary");
                setButtonText("Start Recording");
                setRecording(false);
                clearTimeout(timerId);
                setPreparationProgress(0);
                setRecordingProgress(0);
                count = 0;
            }, TOTAL_DURATION);
            setRecording(true);
        }
    };

    return (
        <div className="d-flex-vertical form">
            <Label>Subject ID</Label>
            <Input
                id="subjectId"
                name="subject-id"
                placeholder="Unique ID of the Subject. Example: 007"
                type="text"
                value={subjectId}
                onChange={(e) => setSubjectId(e.target.value)}
            />
            <br />
            <GestureSelector gesture={gesture} setGesture={setGesture} />
            <br />
            <Button
                className="w-100"
                color={submitBtnColor}
                onClick={onSubmitClick}
            >
                {buttonText}
            </Button>
            <Collapse isOpen={isRecording}>
                <ProgressBar
                    preparationProgress={preparationProgress}
                    recordingProgress={recordingProgress}
                />
            </Collapse>
        </div>
    );
}