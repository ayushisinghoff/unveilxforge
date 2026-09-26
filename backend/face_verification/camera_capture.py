import cv2

def capture_selfie(output_path="test_images/live_selfie.jpg"):
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("ERROR: Camera open nahi ho raha.")
        return False

    print("Camera started.")
    print("Face camera ke saamne rakho.")
    print("Photo capture karne ke liye SPACE press karo.")
    print("Exit ke liye Q press karo.")

    while True:
        ret, frame = camera.read()

        if not ret:
            print("ERROR: Camera frame nahi mil raha.")
            break

        cv2.imshow("Live Face Capture", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == 32:  # SPACE
            cv2.imwrite(output_path, frame)
            print(f"Selfie saved: {output_path}")
            break

        elif key == ord("q"):
            print("Camera closed.")
            break

    camera.release()
    cv2.destroyAllWindows()

    return True


if __name__ == "__main__":
    capture_selfie()