function [ im ] = FrameFromMov( filename, framenum )
    movi = VideoReader(filename);
    im = read(movi, framenum);
    %close(movi);
end

