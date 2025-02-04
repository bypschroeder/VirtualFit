import { create } from "zustand";

interface FormState {
	gender: "male" | "female" | undefined;
	height: number;
	color: string;
	setGender: (gender: "male" | "female" | undefined) => void;
	setHeight: (height: number) => void;
	setColor: (color: string) => void;
}

const useFormStore = create<FormState>((set) => ({
	gender: undefined,
	height: 0,
	color: "#C2C2C2",
	setGender: (gender) => set({ gender }),
	setHeight: (height) => set({ height }),
	setColor: (color) => set({ color }),
}));

export default useFormStore;
