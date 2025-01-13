import { create } from "zustand";

interface FormState {
	gender: "male" | "female" | undefined;
	height: number;
	weight: number;
	setGender: (gender: "male" | "female" | undefined) => void;
	setHeight: (height: number) => void;
	setWeight: (weight: number) => void;
}

const useFormStore = create<FormState>((set) => ({
	gender: undefined,
	height: 0,
	weight: 0,
	setGender: (gender) => set({ gender }),
	setHeight: (height) => set({ height }),
	setWeight: (weight) => set({ weight }),
}));

export default useFormStore;
