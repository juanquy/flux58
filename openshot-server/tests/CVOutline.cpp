/**
 * @file
 * @brief Unit tests for OpenCV Outline effect
 * @author Jonathan Thomas <jonathan@openshot.org>
 *
 * @ref License
 */

// Copyright (c) 2008-2025 OpenShot Studios, LLC
//
// SPDX-License-Identifier: LGPL-3.0-or-later

#include <sstream>
#include <memory>
#include <cmath>

#include "openshot_catch.h"

#include "Clip.h"
#include "effects/Outline.h"

using namespace openshot;

TEST_CASE( "Outline_Tests", "[libopenshot][opencv][outline]" )
{
    // Create a video clip
    std::stringstream path;
    path << TEST_MEDIA_PATH << "1F0CF.svg";

    // Open clip
    openshot::Clip c(path.str());
    c.Open();
    auto f = c.GetFrame(1);

    // Create effect constructor (default values)
    openshot::Outline e1{};

    // Get frame from effect
    auto f1 = e1.GetFrame(f, 1);
    std::shared_ptr<QImage> i1 = f1->GetImage();

    // Check effect colors
    QColor pix1 = i1->pixelColor(3, 32);
    QColor compare1{0, 0, 0, 0};
    CHECK(pix1 == compare1);

    // Test another effect constructor
    openshot::Outline e2(Keyframe(3.0), Color(0, 0, 255, 128));

    // Get frame from effect
    auto f2 = e2.GetFrame(f, 1);
    std::shared_ptr<QImage> i2 = f2->GetImage();

    // Check effect colors
    QColor pix2 = i2->pixelColor(11, 35);
    QColor compare2{0, 0, 255, 128};
    CHECK(pix2 == compare2);

    // Close clip
    c.Close();
}
